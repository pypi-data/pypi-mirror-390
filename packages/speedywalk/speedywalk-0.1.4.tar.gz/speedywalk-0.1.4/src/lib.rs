use std::path::PathBuf;
use std::sync::Arc;
use std::thread;

use crossbeam::channel;
use globset::{Glob, GlobSetBuilder};
use ignore::WalkBuilder;
use pyo3::prelude::*;

#[pyclass]
#[derive(Clone)]
pub struct DirEntry {
    #[pyo3(get)]
    path: String,
    #[pyo3(get)]
    is_file: bool,
    #[pyo3(get)]
    is_dir: bool,
    #[pyo3(get)]
    is_symlink: bool,
}

enum WalkResult {
    Entry(DirEntry),
    Error(String),
}

#[pyclass]
pub struct WalkIterator {
    receiver: channel::Receiver<WalkResult>,
}

#[pymethods]
impl WalkIterator {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&mut self) -> PyResult<Option<DirEntry>> {
        match self.receiver.recv().ok() {
            Some(WalkResult::Entry(entry)) => Ok(Some(entry)),
            Some(WalkResult::Error(err)) => Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(err)),
            None => Ok(None),
        }
    }
}

#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn walk(
    root: String,
    filters: Vec<String>,
    ignore_dirs: Vec<String>,
    ignore_hidden: bool,
    respect_git_ignore: bool,
    respect_global_git_ignore: bool,
    respect_git_exclude: bool,
    respect_ignore: bool,
    follow_symlinks: bool,
    max_depth: Option<usize>,
    min_depth: Option<usize>,
    max_filesize: Option<u64>,
    threads: usize,
) -> PyResult<WalkIterator> {
    let root_path = PathBuf::from(root);

    let mut builder = WalkBuilder::new(&root_path);

    builder
        .hidden(ignore_hidden)
        .git_ignore(respect_git_ignore)
        .git_global(respect_global_git_ignore)
        .git_exclude(respect_git_exclude)
        .ignore(respect_ignore)
        .require_git(false)
        .follow_links(follow_symlinks)
        .threads(threads);

    if let Some(depth) = max_depth {
        builder.max_depth(Some(depth));
    }

    if let Some(depth) = min_depth {
        builder.min_depth(Some(depth));
    }

    if let Some(size) = max_filesize {
        builder.max_filesize(Some(size));
    }

    // Build glob matcher for filters
    let glob_matcher = if !filters.is_empty() {
        let mut glob_builder = GlobSetBuilder::new();
        for filter in &filters {
            let glob = Glob::new(filter)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
            glob_builder.add(glob);
        }
        Some(Arc::new(glob_builder.build().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())
        })?))
    } else {
        None
    };

    // Add ignore directories - collect all paths first
    let ignore_paths: Vec<PathBuf> = ignore_dirs
        .into_iter()
        .map(|ignore_dir| {
            if PathBuf::from(&ignore_dir).is_absolute() {
                PathBuf::from(ignore_dir)
            } else {
                root_path.join(ignore_dir)
            }
        })
        .collect();

    // Apply a single filter that checks all ignore paths
    if !ignore_paths.is_empty() {
        builder.filter_entry(move |entry| {
            // Filter out directories that match any ignore path
            if entry.file_type().is_some_and(|ft| ft.is_dir()) {
                !ignore_paths
                    .iter()
                    .any(|ignore_path| entry.path() == ignore_path)
            } else {
                true
            }
        });
    }

    // Create a bounded channel for parallel walking
    // Buffer size of 10000 provides good throughput while limiting memory usage
    let (sender, receiver) = channel::bounded(10000);

    // Spawn a thread to do the walking
    thread::spawn(move || {
        builder.build_parallel().run(|| {
            let sender = sender.clone();
            let glob_matcher = glob_matcher.clone();
            Box::new(move |result| {
                match result {
                    Ok(entry) => {
                        let path = entry.path();

                        // Apply glob filters if present
                        if let Some(ref glob_set) = glob_matcher
                            && !glob_set.is_match(path)
                        {
                            return ignore::WalkState::Continue;
                        }

                        let file_type = entry.file_type();
                        let dir_entry = DirEntry {
                            path: path.to_string_lossy().to_string(),
                            is_file: file_type.as_ref().is_some_and(|ft| ft.is_file()),
                            is_dir: file_type.as_ref().is_some_and(|ft| ft.is_dir()),
                            is_symlink: file_type.as_ref().is_some_and(|ft| ft.is_symlink()),
                        };
                        let _ = sender.send(WalkResult::Entry(dir_entry));
                    }
                    Err(err) => {
                        let _ = sender.send(WalkResult::Error(err.to_string()));
                    }
                }
                ignore::WalkState::Continue
            })
        });
    });

    Ok(WalkIterator { receiver })
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<DirEntry>()?;
    m.add_class::<WalkIterator>()?;
    m.add_function(wrap_pyfunction!(walk, m)?)?;
    Ok(())
}
