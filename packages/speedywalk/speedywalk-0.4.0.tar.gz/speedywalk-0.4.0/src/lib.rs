use std::path::PathBuf;
use std::sync::Arc;
use std::thread;

use crossbeam::channel;
use globset::GlobSetBuilder;
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
    filter: Vec<String>,
    exclude: Vec<String>,
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

    // Build glob matcher for filter
    let filter_glob_matcher = if !filter.is_empty() {
        let mut glob_builder = GlobSetBuilder::new();
        for pattern in &filter {
            let glob = globset::GlobBuilder::new(pattern)
                .literal_separator(true)
                .build()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
            glob_builder.add(glob);
        }
        Some(Arc::new(glob_builder.build().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())
        })?))
    } else {
        None
    };

    // Build glob matcher for exclude patterns
    let exclude_glob_matcher = if !exclude.is_empty() {
        let mut glob_builder = GlobSetBuilder::new();
        for pattern in &exclude {
            let glob = globset::GlobBuilder::new(pattern)
                .literal_separator(true)
                .build()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
            glob_builder.add(glob);
        }
        Some(Arc::new(glob_builder.build().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())
        })?))
    } else {
        None
    };

    // Apply exclude filter if patterns are provided
    if let Some(ref glob) = exclude_glob_matcher {
        let glob = glob.clone();
        let root_for_exclude = root_path.clone();
        builder.filter_entry(move |entry| {
            // Exclude entries that match any exclude pattern
            // Use relative path for glob matching
            let relative_path = entry
                .path()
                .strip_prefix(&root_for_exclude)
                .unwrap_or(entry.path());
            !glob.is_match(relative_path)
        });
    }

    // Create a bounded channel for parallel walking
    // Buffer size of 10000 provides good throughput while limiting memory usage
    let (sender, receiver) = channel::bounded(10000);

    // Clone root path for use in the closure
    let root_for_matching = root_path.clone();

    // Spawn a thread to do the walking
    thread::spawn(move || {
        builder.build_parallel().run(|| {
            let sender = sender.clone();
            let filter_glob_matcher = filter_glob_matcher.clone();
            let root_for_matching = root_for_matching.clone();
            Box::new(move |result| {
                match result {
                    Ok(entry) => {
                        let path = entry.path();

                        // Get relative path for glob matching
                        let relative_path = path.strip_prefix(&root_for_matching).unwrap_or(path);

                        // Apply glob filters if present
                        if let Some(ref glob) = filter_glob_matcher
                            && !glob.is_match(relative_path)
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
