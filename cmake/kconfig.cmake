
# Create configuration directory
set(CONFIG_OUTPUT_DIR ${CMAKE_BINARY_DIR}/config)
file(MAKE_DIRECTORY ${CONFIG_OUTPUT_DIR})

set(KCONFIG_INPUT  Kconfig)
set(CONFIG_PROJECT sdkconfig)
set(CONFIG_DEFAULT sdkconfig.defaults)

set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${CONFIG_PROJECT} ${CONFIG_DEFAULT})

set(kconfiggen_basecommand
    ${PYTHON_EXECUTABLE}
    ${SCRIPTS_DIR}/kconfiggen.py
    --kconfig ${KCONFIG_INPUT}
    --config ${CONFIG_PROJECT}
    --defaults ${CONFIG_DEFAULT}
)

add_custom_target(menuconfig
    COMMAND ${kconfiggen_basecommand} --menuconfig
    WORKING_DIRECTORY ${PROJECT_DIR}
    VERBATIM
    USES_TERMINAL
)

execute_process(
    COMMAND
    ${kconfiggen_basecommand}
    --output cmake ${CONFIG_OUTPUT_DIR}/sdkconfig.cmake
    --output header ${CONFIG_OUTPUT_DIR}/sdkconfig.h
    --output config ${CONFIG_PROJECT}
    WORKING_DIRECTORY ${PROJECT_DIR}
    RESULT_VARIABLE config_result
)

if(config_result)
    message(FATAL_ERROR "Failed to run kconfgen. Error ${config_result}")
endif()

# include auto generated sdkconfig cmake
include(${CONFIG_OUTPUT_DIR}/sdkconfig.cmake)
include_directories(${CONFIG_OUTPUT_DIR})
