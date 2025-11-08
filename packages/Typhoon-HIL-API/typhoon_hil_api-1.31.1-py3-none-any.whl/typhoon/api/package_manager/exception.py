#
# Package manager API exceptions module.
#
#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# Package manager API exception codes.
PKM_PACKAGE_ALREADY_INSTALLED = 4000
PKM_PACKAGE_NOT_FOUND = 4001
PKM_PACKAGE_CORRUPTED = 4002
PKM_PACKAGE_NAME_INVALID = 4003
PKM_PACKAGE_LIBS_MISSING = 4004
PKM_PACKAGE_EXAMPLES_MISSING = 4005
PKM_EXAMPLE_TITLE_INVALID = 4006
PKM_EXAMPLE_MODEL_MISSING = 4007
PKM_EXAMPLE_MODEL_NOT_FOUND = 4008
PKM_EXAMPLE_MODEL_INVALID = 4009
PKM_EXAMPLE_PANEL_MISSING = 4010
PKM_EXAMPLE_PANEL_NOT_FOUND = 4011
PKM_EXAMPLE_PANEL_INVALID = 4012
PKM_EXAMPLE_IMAGE_NOT_FOUND = 4013
PKM_EXAMPLE_IMAGE_INVALID = 4014
PKM_EXAMPLE_APPLICATION_NOTE_NOT_FOUND = 4015
PKM_EXAMPLE_APPLICATION_NOTE_INVALID = 4016
PKM_EXAMPLE_TEST_NOT_FOUND = 4017
PKM_EXAMPLE_RESOURCE_NOT_FOUND = 4018
PKM_TYPE_MISSMATCH = 4019
PKM_OUTPUT_NOT_EMPTY = 4020
PKM_PACKAGE_VERSION_INVALID = 4021
PKM_PACKAGE_LIBRARY_PATH_NOT_FOUND = 4022
PKM_PACKAGE_LIBRARY_RESOURCE_PATH_NOT_FOUND = 4023
PKM_PACKAGE_ADDITIONAL_FILE_PATH_NOT_FOUND = 4024
PKM_PACKAGE_DOCUMENTATION_FILE_PATH_NOT_FOUND = 4025
PKM_PACKAGE_RELEASE_NOTES_NOT_FOUND = 4026
PKM_PACKAGE_RELEASE_NOTES_FILE_INVALID = 4027
PKM_PACKAGE_LANDING_PAGE_NOT_FOUND = 4028
PKM_PACKAGE_LANDING_PAGE_INVALID = 4029
PKM_PACKAGE_LANDING_PAGE_NOT_ADDED_AS_DOC = 4030
PKM_PACKAGE_PYTHON_PACKAGE_INVALID = 4031
PKM_EXAMPLE_INVALID = 4032
PKM_EXAMPLE_NOT_FOUND = 4033
PKM_EXAMPLE_MODELS_MISSING = 4034
PKM_EXAMPLE_TESTS_MISSING = 4035
PKM_EXAMPLE_METADATA_MISSING = 4036
PKM_EXAMPLE_CORRUPTED = 4037
PKM_PACKAGE_ALREADY_EXISTS = 4038
PKM_PACKAGE_MARKETPLACE_COMMUNICATION_FAIL = 4039
PKM_PACKAGE_OUTPUT_FILE_INVALID = 4040
PKM_MINIMAL_SW_VERSION_INVALID = 4041
PKM_PACKAGE_NOT_SUPPORTED = 4042
PKM_PACKAGE_FILENAME_INVALID = 4043
PKM_PACKAGE_ICON_NOT_FOUND = 4044
PKM_PACKAGE_ICON_FILE_INVALID = 4045
PKM_PACKAGE_VERSION_PRODUCTION_INVALID = 4046


class PkmApiException(Exception):
    """
    Base Package Manager API exception.
    """

    def __init__(self, message, internal_code=None):
        """
        Initialize an object.
        """
        super().__init__(message)
        self.internal_code = internal_code


class PackageAlreadyInstalledException(PkmApiException):
    """
    Package manager exception - package already installed
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_ALREADY_INSTALLED)


class PackageNotFoundException(PkmApiException):
    """
    Package manager exception - package file not found
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_NOT_FOUND)


class PackageCorruptedException(PkmApiException):
    """
    Package manager exception - package file format is corrupted
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_CORRUPTED)


class PackageLibsMissingException(PkmApiException):
    """
    Package manager exception - package libs folder is missing
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_LIBS_MISSING)


class PackageExamplesMissingException(PkmApiException):
    """
    Package manager exception - package examples folder is missing
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_EXAMPLES_MISSING)


class PackageNameInvalidException(PkmApiException):
    """
    Package manager exception - package name contains invalid characters
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_NAME_INVALID)


class ExampleTitleInvalidException(PkmApiException):
    """
    Package manager exception - example title is invalid
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_TITLE_INVALID)


class ModelFileMissing(PkmApiException):
    """
    Package manager exception - example model file is missing
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_MODEL_MISSING)


class ModelNotFoundException(PkmApiException):
    """
    Package manager exception - example model file not found
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_MODEL_NOT_FOUND)


class ModelFileInvalidException(PkmApiException):
    """
    Package manager exception - example model file is invalid
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_MODEL_INVALID)


class PanelFileMissing(PkmApiException):
    """
    Package manager exception - example panel file is missing
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_PANEL_MISSING)


class PanelNotFoundException(PkmApiException):
    """
    Package manager exception - example panel file doesn't exist
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_PANEL_NOT_FOUND)


class PanelFileInvalidException(PkmApiException):
    """
    Package manager exception - example panel file is not valid
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_PANEL_INVALID)


class ImageNotFoundException(PkmApiException):
    """
    Package manager exception - example image file doesn't exist
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_IMAGE_NOT_FOUND)


class ImageFileInvalidException(PkmApiException):
    """
    Package manager exception - example image file is not valid
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_IMAGE_INVALID)


class ApplicationNoteNotFoundException(PkmApiException):
    """
    Package manager exception - example application note doesn't exist
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_APPLICATION_NOTE_NOT_FOUND)


class ApplicationNoteFileInvalidException(PkmApiException):
    """
    Package manager exception - example application note file is invalid
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_APPLICATION_NOTE_INVALID)


class TestFileNotFoundException(PkmApiException):
    """
    Package manager exception - example test file doesn't exist
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_TEST_NOT_FOUND)


class ResourceFileNotFoundException(PkmApiException):
    """
    Package manager exception - resource test file doesn't exist
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_RESOURCE_NOT_FOUND)


class ParameterTypeMissmatchException(PkmApiException):
    """
    Package manager exception - create example parameter type missmatch
    """

    def __init__(self, message):
        super().__init__(message, PKM_TYPE_MISSMATCH)


class OutputDirectoryIsNotEmptyException(PkmApiException):
    """
    Package manager exception - output directory is not empty
    """

    def __init__(self, message):
        super().__init__(message, PKM_OUTPUT_NOT_EMPTY)


class PackageVersionInvalidException(PkmApiException):
    """
    Package manager exception - package version is invalid
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_VERSION_INVALID)


class LibraryPathNotFoundException(PkmApiException):
    """
    Package manager exception - library path not found
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_LIBRARY_PATH_NOT_FOUND)


class LibraryResourcePathNotFoundException(PkmApiException):
    """
    Package manager exception - library resource path not found
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_LIBRARY_RESOURCE_PATH_NOT_FOUND)


class AdditionalFilePathNotFoundException(PkmApiException):
    """
    Package manager exception - additional file path not found
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_ADDITIONAL_FILE_PATH_NOT_FOUND)


class DocumentationFilePathNotFoundException(PkmApiException):
    """
    Package manager exception - documentation file path not found
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_DOCUMENTATION_FILE_PATH_NOT_FOUND)


class ReleaseNotesNotFoundException(PkmApiException):
    """
    Package manager exception - release notes file does not exist
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_RELEASE_NOTES_NOT_FOUND)


class ReleaseNotesFileInvalidException(PkmApiException):
    """
    Package manager exception - release notes file is not valid
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_RELEASE_NOTES_FILE_INVALID)


class DocumentationLandingPageNotFoundException(PkmApiException):
    """
    Package manager exception - landing page file does not exist
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_LANDING_PAGE_NOT_FOUND)


class DocumentationLandingPageInvalidException(PkmApiException):
    """
    Package manager exception - landing page file is not valid
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_LANDING_PAGE_INVALID)


class DocumentationLandingPageNotAddedAsDocumentation(PkmApiException):
    """
    Package manager exception - landing page not added to list of documentation
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_LANDING_PAGE_NOT_ADDED_AS_DOC)


class PythonPackageInvalidException(PkmApiException):
    """
    Package manager exception - python package is not valid
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_PYTHON_PACKAGE_INVALID)


class ExampleNotValidException(PkmApiException):
    """
    Package manager exception - example is not valid
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_INVALID)


class ExampleNotFoundException(PkmApiException):
    """
    Package manager exception - example not found
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_NOT_FOUND)


class ExampleModelsMissingException(PkmApiException):
    """
    Package manager exception - models folder missing from example
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_MODELS_MISSING)


class ExampleTestsMissingException(PkmApiException):
    """
    Package manager exception - tests folder missing from example
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_TESTS_MISSING)


class ExampleMetadataMissingException(PkmApiException):
    """
    Package manager exception - metadata file missing from example
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_METADATA_MISSING)


class ExampleCorruptedException(PkmApiException):
    """
    Package manager exception - landing page file does not exist
    """

    def __init__(self, message):
        super().__init__(message, PKM_EXAMPLE_CORRUPTED)


class PackageAlreadyExistsException(PkmApiException):
    """
    Package manager exception - package already exists
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_ALREADY_EXISTS)


class PackageMarketplaceCommunicationException(PkmApiException):
    """
    Package manager exception - communication with remote repository server fail
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_MARKETPLACE_COMMUNICATION_FAIL)


class PackageOutputFileInvalidException(PkmApiException):
    """
    Package manager exception - package output file is invalid
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_OUTPUT_FILE_INVALID)


class PackageMinimalSwVersionInvalidException(PkmApiException):
    """
    Package manager exception - minimal software version is invalid
    """

    def __init__(self, message):
        super().__init__(message, PKM_MINIMAL_SW_VERSION_INVALID)


class PackageNotSupportedOnCurrentSoftwareVersionException(PkmApiException):
    """
    Package manager exception - package not supported on current software version
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_NOT_SUPPORTED)


class PackageFileNameInvalidException(PkmApiException):
    """
    Package manager exception - package filename has invalid extension
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_FILENAME_INVALID)


class IconNotFoundException(PkmApiException):
    """
    Package manager exception - icon file not found
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_ICON_NOT_FOUND)


class IconFileInvalidException(PkmApiException):
    """
    Package manager exception - icon file is not valid
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_ICON_FILE_INVALID)


class PackageVersionCannotPublishException(PkmApiException):
    """
    Package manager exception - package version is invalid
    """

    def __init__(self, message):
        super().__init__(message, PKM_PACKAGE_VERSION_PRODUCTION_INVALID)


# Mapping from error code to exception class
EXCEPTION_MAP = {
    PKM_PACKAGE_ALREADY_INSTALLED: PackageAlreadyInstalledException,
    PKM_PACKAGE_NOT_FOUND: PackageNotFoundException,
    PKM_PACKAGE_CORRUPTED: PackageCorruptedException,
    PKM_PACKAGE_NAME_INVALID: PackageNameInvalidException,
    PKM_PACKAGE_LIBS_MISSING: PackageLibsMissingException,
    PKM_PACKAGE_EXAMPLES_MISSING: PackageExamplesMissingException,
    PKM_EXAMPLE_TITLE_INVALID: ExampleTitleInvalidException,
    PKM_EXAMPLE_MODEL_MISSING: ModelFileMissing,
    PKM_EXAMPLE_MODEL_NOT_FOUND: ModelNotFoundException,
    PKM_EXAMPLE_MODEL_INVALID: ModelFileInvalidException,
    PKM_EXAMPLE_PANEL_MISSING: PanelFileMissing,
    PKM_EXAMPLE_PANEL_NOT_FOUND: PanelNotFoundException,
    PKM_EXAMPLE_PANEL_INVALID: PanelFileInvalidException,
    PKM_EXAMPLE_IMAGE_NOT_FOUND: ImageNotFoundException,
    PKM_EXAMPLE_IMAGE_INVALID: ImageFileInvalidException,
    PKM_EXAMPLE_APPLICATION_NOTE_NOT_FOUND: ApplicationNoteNotFoundException,
    PKM_EXAMPLE_APPLICATION_NOTE_INVALID: ApplicationNoteFileInvalidException,
    PKM_EXAMPLE_TEST_NOT_FOUND: TestFileNotFoundException,
    PKM_EXAMPLE_RESOURCE_NOT_FOUND: ResourceFileNotFoundException,
    PKM_TYPE_MISSMATCH: ParameterTypeMissmatchException,
    PKM_OUTPUT_NOT_EMPTY: OutputDirectoryIsNotEmptyException,
    PKM_PACKAGE_VERSION_INVALID: PackageVersionInvalidException,
    PKM_PACKAGE_LIBRARY_PATH_NOT_FOUND: LibraryPathNotFoundException,
    PKM_PACKAGE_LIBRARY_RESOURCE_PATH_NOT_FOUND: LibraryResourcePathNotFoundException,
    PKM_PACKAGE_ADDITIONAL_FILE_PATH_NOT_FOUND: AdditionalFilePathNotFoundException,
    PKM_PACKAGE_DOCUMENTATION_FILE_PATH_NOT_FOUND: DocumentationFilePathNotFoundException,
    PKM_PACKAGE_RELEASE_NOTES_NOT_FOUND: ReleaseNotesNotFoundException,
    PKM_PACKAGE_RELEASE_NOTES_FILE_INVALID: ReleaseNotesFileInvalidException,
    PKM_PACKAGE_LANDING_PAGE_NOT_FOUND: DocumentationLandingPageNotFoundException,
    PKM_PACKAGE_LANDING_PAGE_INVALID: DocumentationLandingPageInvalidException,
    PKM_PACKAGE_LANDING_PAGE_NOT_ADDED_AS_DOC: DocumentationLandingPageNotAddedAsDocumentation,
    PKM_PACKAGE_PYTHON_PACKAGE_INVALID: PythonPackageInvalidException,
    PKM_EXAMPLE_INVALID: ExampleNotValidException,
    PKM_EXAMPLE_NOT_FOUND: ExampleNotFoundException,
    PKM_EXAMPLE_MODELS_MISSING: ExampleModelsMissingException,
    PKM_EXAMPLE_TESTS_MISSING: ExampleTestsMissingException,
    PKM_EXAMPLE_METADATA_MISSING: ExampleMetadataMissingException,
    PKM_EXAMPLE_CORRUPTED: ExampleCorruptedException,
    PKM_PACKAGE_ALREADY_EXISTS: PackageAlreadyExistsException,
    PKM_PACKAGE_MARKETPLACE_COMMUNICATION_FAIL: PackageMarketplaceCommunicationException,
    PKM_PACKAGE_OUTPUT_FILE_INVALID: PackageOutputFileInvalidException,
    PKM_MINIMAL_SW_VERSION_INVALID: PackageMinimalSwVersionInvalidException,
    PKM_PACKAGE_NOT_SUPPORTED: PackageNotSupportedOnCurrentSoftwareVersionException,
    PKM_PACKAGE_FILENAME_INVALID: PackageFileNameInvalidException,
    PKM_PACKAGE_ICON_NOT_FOUND: IconNotFoundException,
    PKM_PACKAGE_ICON_FILE_INVALID: IconFileInvalidException,
    PKM_PACKAGE_VERSION_PRODUCTION_INVALID: PackageVersionCannotPublishException,
}


def get_exception_by_code(code, message=None):
    exc_class = EXCEPTION_MAP.get(code, PkmApiException)
    return exc_class(message)
