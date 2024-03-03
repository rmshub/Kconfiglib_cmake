include_guard(GLOBAL)

# On Windows, instruct Python to output UTF-8 even when not
# interacting with a terminal. This is required since Python scripts
# are invoked by CMake code and, on Windows, standard I/O encoding defaults
# to the current code page if not connected to a terminal, which is often
# not what we want.
if (WIN32)
  set(ENV{PYTHONIOENCODING} "utf-8")
endif()

set(PYTHON_MINIMUM_REQUIRED 3.8)

foreach(candidate "python" "python3")
    find_program(Python3_EXECUTABLE ${candidate})
        if(Python3_EXECUTABLE)
            execute_process (COMMAND "${Python3_EXECUTABLE}" -c
                                    "import sys; sys.stdout.write('.'.join([str(x) for x in sys.version_info[:2]]))"
                            RESULT_VARIABLE result
                            OUTPUT_VARIABLE version
                            OUTPUT_STRIP_TRAILING_WHITESPACE)

        if(version VERSION_LESS PYTHON_MINIMUM_REQUIRED)
        set(Python3_EXECUTABLE "Python3_EXECUTABLE-NOTFOUND")
            message(FATAL_ERROR "Python3 is not found")
        endif()
    endif()
endforeach()

set(PYTHON_EXECUTABLE ${Python3_EXECUTABLE})