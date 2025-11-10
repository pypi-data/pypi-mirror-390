# Fix

## Error of building wheel

```
2025-11-10T06:11:31.5975082Z * Building wheel...
2025-11-10T06:11:31.7163359Z Traceback (most recent call last):
2025-11-10T06:11:31.7164519Z   File "/home/runner/.local/lib/python3.12/site-packages/pyproject_hooks/_in_process/_in_process.py", line 389, in <module>
2025-11-10T06:11:31.7165429Z     main()
2025-11-10T06:11:31.7166218Z   File "/home/runner/.local/lib/python3.12/site-packages/pyproject_hooks/_in_process/_in_process.py", line 373, in main
2025-11-10T06:11:31.7167337Z     json_out["return_val"] = hook(**hook_input["kwargs"])
2025-11-10T06:11:31.7167777Z                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-10T06:11:31.7168649Z   File "/home/runner/.local/lib/python3.12/site-packages/pyproject_hooks/_in_process/_in_process.py", line 280, in build_wheel
2025-11-10T06:11:31.7169546Z     return _build_backend().build_wheel(
2025-11-10T06:11:31.7169852Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-10T06:11:31.7170566Z   File "/tmp/build-env-48nm3ixt/lib/python3.12/site-packages/hatchling/build.py", line 58, in build_wheel
2025-11-10T06:11:31.7171773Z     return os.path.basename(next(builder.build(directory=wheel_directory, versions=['standard'])))
2025-11-10T06:11:31.7172773Z                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-10T06:11:31.7173470Z   File "/tmp/build-env-48nm3ixt/lib/python3.12/site-packages/hatchling/builders/plugin/interface.py", line 155, in build
2025-11-10T06:11:31.7174214Z     artifact = version_api[version](directory, **build_data)
2025-11-10T06:11:31.7174762Z                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-10T06:11:31.7175402Z   File "/tmp/build-env-48nm3ixt/lib/python3.12/site-packages/hatchling/builders/wheel.py", line 477, in build_standard
2025-11-10T06:11:31.7176090Z     for included_file in self.recurse_included_files():
2025-11-10T06:11:31.7176876Z   File "/tmp/build-env-48nm3ixt/lib/python3.12/site-packages/hatchling/builders/plugin/interface.py", line 176, in recurse_included_files
2025-11-10T06:11:31.7177662Z     yield from self.recurse_selected_project_files()
2025-11-10T06:11:31.7178307Z   File "/tmp/build-env-48nm3ixt/lib/python3.12/site-packages/hatchling/builders/plugin/interface.py", line 180, in recurse_selected_project_files
2025-11-10T06:11:31.7178893Z     if self.config.only_include:
2025-11-10T06:11:31.7179111Z        ^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-10T06:11:31.7179381Z   File "/usr/lib/python3.12/functools.py", line 995, in __get__
2025-11-10T06:11:31.7229581Z     val = self.func(instance)
2025-11-10T06:11:31.7230045Z           ^^^^^^^^^^^^^^^^^^^
2025-11-10T06:11:31.7231012Z   File "/tmp/build-env-48nm3ixt/lib/python3.12/site-packages/hatchling/builders/config.py", line 713, in only_include
2025-11-10T06:11:31.7232624Z     only_include = only_include_config.get('only-include', self.default_only_include()) or self.packages
2025-11-10T06:11:31.7233542Z                                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-10T06:11:31.7234415Z   File "/tmp/build-env-48nm3ixt/lib/python3.12/site-packages/hatchling/builders/wheel.py", line 262, in default_only_include
2025-11-10T06:11:31.7235641Z     return self.default_file_selection_options.only_include
2025-11-10T06:11:31.7236244Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-10T06:11:31.7236849Z   File "/usr/lib/python3.12/functools.py", line 995, in __get__
2025-11-10T06:11:31.7237452Z     val = self.func(instance)
2025-11-10T06:11:31.7237793Z           ^^^^^^^^^^^^^^^^^^^
2025-11-10T06:11:31.7238653Z   File "/tmp/build-env-48nm3ixt/lib/python3.12/site-packages/hatchling/builders/wheel.py", line 250, in default_file_selection_options
2025-11-10T06:11:31.7239588Z     raise ValueError(message)
2025-11-10T06:11:31.7240302Z ValueError: Unable to determine which files to ship inside the wheel using the following heuristics: https://hatch.pypa.io/latest/plugins/builder/wheel/#default-file-selection
2025-11-10T06:11:31.7242992Z 
2025-11-10T06:11:31.7243446Z The most likely cause of this is that there is no directory that matches the name of your project (tpdp_pydantic_v2).
2025-11-10T06:11:31.7244078Z 
2025-11-10T06:11:31.7244724Z At least one file selection option must be defined in the `tool.hatch.build.targets.wheel` table, see: https://hatch.pypa.io/latest/config/build/
2025-11-10T06:11:31.7245509Z 
2025-11-10T06:11:31.7246204Z As an example, if you intend to ship a directory named `foo` that resides within a `src` directory located at the root of your project, you can define the following:
2025-11-10T06:11:31.7247013Z 
2025-11-10T06:11:31.7247169Z [tool.hatch.build.targets.wheel]
2025-11-10T06:11:31.7247531Z packages = ["src/foo"]
2025-11-10T06:11:31.7425293Z 
2025-11-10T06:11:31.7427104Z ERROR Backend subprocess exited when trying to invoke build_wheel
2025-11-10T06:11:31.7581774Z ##[error]Process completed with exit code 1.
```