
import os
from PlatformConnectors.PackageMaker import PackageAutomation

package = PackageAutomation.auto_package(os.path.dirname(os.path.abspath(__file__)))

