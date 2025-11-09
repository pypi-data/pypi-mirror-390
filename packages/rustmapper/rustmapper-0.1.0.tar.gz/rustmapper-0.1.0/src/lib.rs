// This file intentionally left minimal.
// The binary crate (main.rs) declares all modules directly.
// No external consumers use this library interface.

#[cfg(feature = "pyo3")]
mod python_bindings;
