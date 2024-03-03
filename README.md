# Kconfiglib with CMake build
CMake build support for [Kconfiglib](https://github.com/ulfalizer/Kconfiglib) library. This project supports CMake and C header file generation from Kconfig file with default configuration support (E.g. Kconfig.defaults).
- Generated CMake and C header files are placed in `${CMAKE_BINARY_DIR}/config`
- CMake file is included to project (to customize build) at [kconfig.cmake](cmake/kconfig.cmake#L42)
- C Header file path is included to project at [kconfig.cmake](cmake/kconfig.cmake#L43)
- Updated configuration file (sdkconfig) generated at project directory

## Prerequisties
- Copy [cmake](cmake) and [scripts](scripts) into project
- Create 'SCRIPTS_DIR' cmake variable with [scripts](scripts) folder location. E.g. `set(SCRIPTS_DIR ${CMAKE_SOURCE_DIR}/scripts)`
- Include python and kconfig in project cmake file. E.g. `include(${CMAKE_SOURCE_DIR}/cmake/python.cmake)` and `include(${CMAKE_SOURCE_DIR}/cmake/Kconfig.cmake)`
- Update below cmake variables if required in [kconfig.cmake](cmake/kconfig.cmake)
```
set(CONFIG_OUTPUT_DIR ${CMAKE_BINARY_DIR}/config)

set(KCONFIG_INPUT  Kconfig)
set(CONFIG_PROJECT sdkconfig)
set(CONFIG_DEFAULT sdkconfig.defaults)
```

## Launch menuconfig
- Run `cmake --build build_output_path --target menuconfig` to launch menuconfig in terminal

## Notes
- Tested with Ubuntu 22.04 and GCC 11.4.0
- Refer [Kconfiglib](https://github.com/ulfalizer/Kconfiglib) for Windows dependencies
