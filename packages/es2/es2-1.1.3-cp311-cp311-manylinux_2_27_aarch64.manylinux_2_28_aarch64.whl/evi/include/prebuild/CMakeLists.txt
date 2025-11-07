set(FLATC_EXECUTABLE $<TARGET_FILE:flatc>)

set(FLATBUFFER_SCHEMAS ${PRE_BUILD_DIR}/DebFBType.fbs)

foreach(fbs_file ${FLATBUFFER_SCHEMAS})
  get_filename_component(fname ${fbs_file} NAME_WE)
  set(generated_header ${PRE_BUILD_DIR}/${fname}.h)

  add_custom_command(
    OUTPUT ${generated_header}
    COMMAND ${FLATC_EXECUTABLE} --cpp -o ${PRE_BUILD_DIR} ${fbs_file}
    COMMAND ${CMAKE_COMMAND} -E rename ${PRE_BUILD_DIR}/${fname}_generated.h
            ${generated_header}
    DEPENDS ${fbs_file}
    COMMENT "Generating cpp flatbuffer from ${fbs_file}")

  list(APPEND GENERATED_HEADERS ${generated_header})
endforeach()

add_custom_target(generate_flatbuffers ALL DEPENDS ${GENERATED_HEADERS})

set(GEN_PARAM_H ${PRE_BUILD_DIR}/DebParam.hpp)
set(IN_JSON ${DEB_PARAMETER_JSON})
add_executable(GenParam ${PRE_BUILD_DIR}/DebGenParam.cpp)
target_include_directories(GenParam
                           PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../external)
message(STATUS "Preset list: ${DEB_PRESET_LIST}")
add_custom_command(
  OUTPUT ${GEN_PARAM_H}
  COMMAND GenParam ${IN_JSON} ${DEB_PRESET_LIST} ${GEN_PARAM_H}
  DEPENDS GenParam ${IN_JSON}
  COMMENT "Generating ${GEN_PARAM_H} via GenParam"
  VERBATIM)

add_custom_target(generated_param_header ALL DEPENDS ${GEN_PARAM_H})
