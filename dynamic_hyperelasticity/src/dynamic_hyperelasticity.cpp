#include <iostream>
#include <cstdlib>

#include "opendihu.h"

int main(int argc, char *argv[])
{
  // 3D Laplace equation 0 = du^2/dx^2 + du^2/dy^2
  
  // initialize everything, handle arguments and parse settings from input file
  DihuContext settings(argc, argv);
  
  TimeSteppingScheme::DynamicHyperelasticitySolver<> equationDiscretized(settings);
  
  equationDiscretized.run();
  
  return EXIT_SUCCESS;
}
