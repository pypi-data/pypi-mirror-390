class PackageManagerAPIBase:
    """
    Base class for Package Manager API (Application Programming Interface)
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize an object.

        Args:
            None
        """
        super().__init__()

    def get_installed_packages(self):
        """
        Returns iterable over installed packages.

        Returns:
            Iterable over installed packages (Package).

        **Example:**

        .. literalinclude:: package_manager_api_examples/get_installed_packages.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/get_installed_packages.example
        """
        raise NotImplementedError()

    def get_available_packages(self, latest_version=True):
        """
        Returns iterable over packages available on Package Marketplace.

        Args:
            latest_version (bool): If true, return only latest version of
            the package. Otherwise, return an object for each version
            of the package available.

        Returns:
            Iterable over available packages (Package).

        **Example:**

        .. literalinclude:: package_manager_api_examples/get_available_packages.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/get_available_packages.example
        """
        raise NotImplementedError()

    def get_modified_packages(self):
        """
        Checks integrity of installed packages. Returns iterable over packages
        that have been modified.

        Returns:
            Iterable over modified packages (Package).

        **Example:**

        .. literalinclude:: package_manager_api_examples/get_modified_packages.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/get_modified_packages.example
        """
        raise NotImplementedError()

    def download_package(self, output_path, package_name, version="latest"):
        """
        Returns iterable over packages available on Package Marketplace.

        Args:
            output_path (str): Output directory/file path for downloaded package.
                If file is passed, it must have .tpkg extension. If not, it will
                have "[package_name]-[version].tpkg" format.
            package_name (str): name of the package to be downloaded.
            version (str): Package version. String "latest" can be used for
            latest version of the package.

        Returns:
            String file path of downloaded package

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/download_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/download_package.example
        """
        raise NotImplementedError()

    def install_package(self, filename):
        """
        Installs a package located at filename, specified by parameter.

        Args:
            filename: filename in which package is located.

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/install_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/install_package.example
        """
        raise NotImplementedError()

    def uninstall_package(self, package_name):
        """
        Uninstalls a package by name, specified by parameter package_name.

        Args:
            package_name: name of the package to be uninstalled.

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/uninstall_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/uninstall_package.example
        """
        raise NotImplementedError()

    def reinstall_package(self, package_name):
        """
        Reinstall a package by name, specified by parameter package_name.

        Args:
            package_name: name of the package to be reinstalled.

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/reinstall_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/reinstall_package.example
        """
        raise NotImplementedError()

    def validate_package(self, filename):
        """
        Validate a package located at filename, specified by parameter.

        Args:
            filename: filename in which package is located.

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/validate_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/validate_package.example
        """
        raise NotImplementedError()

    def create_example(
        self,
        title,
        model_file,
        panel_file,
        output_path,
        tags=None,
        description="",
        image_file="",
        app_note_file="",
        tests=None,
        test_resources=None,
        resources=None,
    ):
        """
        Create an example with given parameters and save it at output_path

        Args:
            title: Example title
            model_file: Path to model file
            panel_file: Path to panel file
            output_path: Path where example will be saved
            tags: List of string tags
            description: Example description
            image_file: Path to image file
            app_note_file: Path to application note document
            tests: List of files representing tests
            test_resources: List of files representing resources used in tests
            resources: List of files representing resources

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/create_example.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/create_example.example
        """
        raise NotImplementedError()

    def create_package(
        self,
        package_name,
        version,
        output_path,
        author="",
        website="",
        description="",
        minimal_sw_version="",
        library_paths=None,
        resource_paths=None,
        example_paths=None,
        additional_files_paths=None,
        python_packages_paths=None,
        documentation_paths=None,
        documentation_landing_page="",
        release_notes_path="",
        icon_path="",
    ):
        """
        Create a package with given parameters and save it at output_path

        Args:
            package_name: Package name
            version: Package version
            output_path: Path where package will be saved. If a directory path is passed, the package will be named "package_name - version.tpkg". If a file path is passed, it must have a .tpkg extension.
            author: Package author
            website: Package author website
            description: Package description
            minimal_sw_version: Minimal version of software in which package is supported
            library_paths: List of paths representing libraries (directories/files)
            resource_paths: List of paths representing library resources (directories/files)
            example_paths: List of paths representing example directories
            additional_files_paths: List of paths representing additional files (directories/files)
            python_packages_paths: List of paths representing python packages (directories/files)
            documentation_paths: List of paths representing package documentation (directories/files)
            documentation_landing_page: Documentation landing page (must be included in documentation_paths)
            release_notes_path: Path to release notes file (html, pdf..)
            icon_path: Path to package icon file (svg, png, jpg, bmp...)

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/create_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/create_package.example
        """
        raise NotImplementedError()
