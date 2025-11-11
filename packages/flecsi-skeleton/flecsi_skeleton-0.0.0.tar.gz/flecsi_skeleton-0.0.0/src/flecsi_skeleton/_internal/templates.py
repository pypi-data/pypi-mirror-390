#################################################################################
# CMakeLists
#################################################################################

#-------------------------------------------------------------------------------#
# Top-Level CMakeLists.txt
#-------------------------------------------------------------------------------#

TOPLEVEL_CMAKELISTS = """\
#-------------------------------------------------------------------------------#
# Top-Level CMakeLists.txt
#-------------------------------------------------------------------------------#

cmake_minimum_required(VERSION 3.20)

project({UCC_APPNAME} LANGUAGES C CXX)

set(CMAKE_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_EXTENSIONS OFF)

#-------------------------------------------------------------------------------#
# Find FleCSI package.
#-------------------------------------------------------------------------------#

find_package(FleCSI 2 REQUIRED)

#-------------------------------------------------------------------------------#
# Add library.
#-------------------------------------------------------------------------------#

set(SPEC_TARGET "${{CMAKE_PROJECT_NAME}}-Spec")
add_library(${{SPEC_TARGET}} INTERFACE)
add_library(${{SPEC_TARGET}}::${{SPEC_TARGET}} ALIAS ${{SPEC_TARGET}})
target_include_directories(${{SPEC_TARGET}}
  INTERFACE
    $<BUILD_INTERFACE:${{CMAKE_CURRENT_SOURCE_DIR}}>
    $<BUILD_INTERFACE:${{CMAKE_BINARY_DIR}}>
    $<INSTALL_INTERFACE:${{CMAKE_INSTALL_INCLUDEDIR}}>
)
add_subdirectory(spec)

#-------------------------------------------------------------------------------#
# Add application.
#-------------------------------------------------------------------------------#

add_subdirectory(app)
"""

#-------------------------------------------------------------------------------#
# Specialization CMakeLists.txt
#-------------------------------------------------------------------------------#

SPEC_CMAKELISTS = """\
#-------------------------------------------------------------------------------#
# Specialization CMakeLists.txt
#-------------------------------------------------------------------------------#

function(spec_headers)
  target_sources(${{SPEC_TARGET}} PUBLIC FILE_SET public_headers TYPE HEADERS
    BASE_DIRS ${{CMAKE_SOURCE_DIR}} FILES ${{ARGN}})
endfunction()

spec_headers(
  control.hh
)
"""

#-------------------------------------------------------------------------------#
# Application CMakeLists.txt
#-------------------------------------------------------------------------------#

APP_CMAKELISTS = """\
#-------------------------------------------------------------------------------#
# {UCC_APPNAME} CMakeLists.txt
#-------------------------------------------------------------------------------#

option({UC_APPNAME}_WRITE_CONTROL_INFO
  "Output the control model graph and actions at startup"
  FleCSI_ENABLE_GRAPHVIZ)
mark_as_advanced({UC_APPNAME}_WRITE_CONTROL_INFO)

add_executable({LC_APPNAME} {LC_APPNAME}.cc)
target_link_libraries({LC_APPNAME} ${{SPEC_TARGET}}::${{SPEC_TARGET}} FleCSI::FleCSI)

if(FleCSI_ENABLE_GRAPHVIZ AND {UC_APPNAME}_WRITE_CONTROL_INFO)
  target_compile_definitions({LC_APPNAME} PUBLIC {UC_APPNAME}_WRITE_CONTROL_INFO)
elseif(NOT FleCSI_ENABLE_GRAPHVIZ AND {UC_APPNAME}_WRITE_CONTROL_INFO)
  message(WARNING,
    "{UC_APPNAME}_WRITE_CONTROL_INFO enabled but FleCSI not compiled with Graphviz")
endif()
"""

#################################################################################
# Specialization source
#################################################################################

#-------------------------------------------------------------------------------#
# Control Model
#-------------------------------------------------------------------------------#

CONTROL = """\
#ifndef SPEC_CONTROL_HH
#define SPEC_CONTROL_HH

#include <flecsi/flog.hh>
#include <flecsi/run/control.hh>

namespace spec::control {{
/// Control Points.
enum class cp {{
  /// Application initialization.
  initialize,
  /// Time evolution (cycled).
  advance,
  /// Running analysis (cycled).
  analyze,
  /// Application finalization.
  finalize
}};

inline const char *
operator*(cp control_point) {{
  switch(control_point) {{
    case cp::initialize:
      return "initialize";
    case cp::advance:
      return "advance";
    case cp::analyze:
      return "analyze";
    case cp::finalize:
      return "finalize";
  }}
  flog_fatal("invalid control point");
}}

struct control_policy : flecsi::run::control_base {{

  using control_points_enum = cp;

  /// Control Model Constructor
  /// @param steps Maximum number of time steps.
  /// @param log   Logging frequency.
  control_policy(std::size_t steps, std::size_t log)
    : steps_(steps), log_(log) {{}}

  auto step() const {{ return step_; }}
  auto steps() const {{ return steps_; }}
  auto log() const {{ return log_; }}

  static bool cycle_control(control_policy & cp) {{
    return cp.step_++ < cp.steps_;
  }}

  using evolve = cycle<cycle_control, point<cp::advance>, point<cp::analyze>>;

  using control_points =
    list<point<cp::initialize>, evolve, point<cp::finalize>>;

protected:
  std::size_t step_{{0}};
  std::size_t steps_;
  std::size_t log_;
}};
}}

#endif // SPEC_CONTROL_HH
"""

#################################################################################
# Application source
#################################################################################

#-------------------------------------------------------------------------------#
# Driver
#-------------------------------------------------------------------------------#

DRIVER = """\
/*-----------------------------------------------------------------------------*
  Driver (main function)
 *-----------------------------------------------------------------------------*/

// These import the action definitions.
#include "advance.hh"
#include "analyze.hh"
#include "initialize.hh"
#include "finalize.hh"

/*
  Headers are ordered by decreasing locality, e.g., directory, project,
  library dependency, standard library.
 */
#include "types.hh"

#include <spec/control.hh>

#include <flecsi/runtime.hh>

using namespace flecsi;

int
main(int argc, char ** argv) {{
  // Output control model information.
#if defined({UC_APPNAME}_WRITE_CONTROL_INFO)
  {LC_APPNAME}::control::write_graph("{UC_APPNAME}", "cm.dot");
  {LC_APPNAME}::control::write_actions("{UC_APPNAME}", "actions.dot");
#endif

  const flecsi::getopt g;
  try {{
    g(argc, argv);
  }}
  catch(const std::logic_error & e) {{
    std::cerr << e.what() << ' ' << g.usage(argc ? argv[0] : "");
    return 1;
  }}

  const run::dependencies_guard dg;
  run::config cfg;

  runtime run(cfg);
  flog::add_output_stream("clog", std::clog, true);
  run.control<{LC_APPNAME}::control>(10, 1);
}}
"""

#-------------------------------------------------------------------------------#
# Advance
#-------------------------------------------------------------------------------#

ADVANCE = """\
#ifndef {UC_APPNAME}_ADVANCE_HH
#define {UC_APPNAME}_ADVANCE_HH

#include "types.hh"

#include <flecsi/flog.hh>

namespace {LC_APPNAME}::action {{

void
advance(control_policy & cp) {{
  flog(info) << "Advance Action: " << cp.step() << std::endl;
}}

inline control::action<advance, cp::advance> advance_action;
}}

#endif // {UC_APPNAME}_ADVANCE_HH
"""

#-------------------------------------------------------------------------------#
# Analyze
#-------------------------------------------------------------------------------#

ANALYZE = """\
#ifndef {UC_APPNAME}_ANALYZE_HH
#define {UC_APPNAME}_ANALYZE_HH

#include "types.hh"

#include <flecsi/flog.hh>

namespace {LC_APPNAME}::action {{

void
analyze(control_policy & cp) {{
  flog(info) << "Analyze Action: " << cp.step() << std::endl;
}}

inline control::action<analyze, cp::analyze> analyze_action;
}}

#endif // {UC_APPNAME}_ANALYZE_HH
"""

#-------------------------------------------------------------------------------#
# Finalize
#-------------------------------------------------------------------------------#

FINALIZE = """\
#ifndef {UC_APPNAME}_FINALIZE_HH
#define {UC_APPNAME}_FINALIZE_HH

#include "types.hh"

#include <flecsi/flog.hh>

namespace {LC_APPNAME}::action {{

void
finalize(control_policy & cp) {{
  flog(info) << "Finalize Action" << std::endl;
}}

inline control::action<finalize, cp::finalize> final_action;
}}

#endif // {UC_APPNAME}_FINALIZE_HH
"""

#-------------------------------------------------------------------------------#
# Initialize
#-------------------------------------------------------------------------------#

INITIALIZE = """\
#ifndef {UC_APPNAME}_INITIALIZE_HH
#define {UC_APPNAME}_INITIALIZE_HH

#include "types.hh"

#include <flecsi/flog.hh>

namespace {LC_APPNAME}::action {{

void
initialize(control_policy & cp) {{
  flog(info) << "Initialize Action" << std::endl;
}}

inline control::action<initialize, cp::initialize> init_action;
}}

#endif // {UC_APPNAME}_INITIALIZE_HH
"""

#-------------------------------------------------------------------------------#
# Types
#-------------------------------------------------------------------------------#

TYPES = """\
#ifndef {UC_APPNAME}_TYPES_HH
#define {UC_APPNAME}_TYPES_HH

#include <spec/control.hh>

namespace {LC_APPNAME} {{

using spec::control::control_policy;
using control = flecsi::run::control<control_policy>;
using cp = spec::control::cp;

}}

#endif // {UC_APPNAME}_TYPES_HH
"""
