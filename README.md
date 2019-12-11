# EdTechHubLib - The EdTech Hub Evidence Library application

This application uses [Kerko] to provide a user-friendly search and browsing
web interface for a bibliography managed with the [Zotero] reference manager.

## About this application

This application is built in [Python] with the [Flask] framework.

Some things to know:

- Although the structure and some bits of code are similar to [KerkoApp]
  (version 0.5), no attempt was made in making this application compatible with
  KerkoApp in any way. Since this application is just a thin layer built over
  Kerko, it is relatively small and can follow its own destiny, separate from
  KerkoApp's.
- Configuration is generally done in `app/config.py`, except for secret keys
  that should _not_ be stored in source control (per the [Twelve-factor
  App](https://12factor.net/config) methodology).
- Some of Kerko's templates are overridden (see the `app/templates/app/`
  directory).
- The custom Sass stylesheet takes advantage of Bootstrap's theming capabilities
  (see `app/static/src/scss/styles.scss`).
- Front-end assets such as CSS, JavaScript and icons are bundled with the
  application. In production, these files are statically served from the
  `app/static/dist/` directory.
- Similarly to back-end Python packages, front-end dependencies are retrieved
  during the installation process. While the former go into your Python virtual
  environment, the latter go to the `app/static/src/vendor/` directory, which
  should not be stored in the code repository.
- If some source assets are modified, you have to run the build process, which
  generates the content of `app/static/dist/` from source assets in
  `app/static/src/`. You normally push the resulting files from
  `app/static/dist/` to the code repository, so that the built assets can be
  used on the production server.

## Developing EdTechHubLib

Making changes to EdTechHubLib requires a Python development environment. Once
the changes are tested in that environment, they can be pushed to the Git
repository and deployed on the production server (see the **Deploying
EdTechHubLib in production** section).

### Installing the application locally

Pre-requisites:

- A Python [virtual environment][virtualenv] using the same Python
  version as the production server (Python 3.7).
- Install [Node.js] (recommended version: 10.x or later). Node.js provides
  [npm], a package manager that is required to install some of the application's
  front-end dependencies.

Steps:

1. With the virtual environment active, install the software by running the
   following shell commands:

   ```bash
   git clone https://github.com/edtechhub/eth-evidence-library-kerko.git edtechhublib
   cd edtechhublib
   pip install -r requirements/dev.txt
   npm install
   ```

   This will install many packages required by Kerko and EdTechHubLib.

2. Copy `dotenv.sample` to `.env`. Open `.env` in a text editor to assign proper
   values to the variables outlined below.

   * `SECRET_KEY`: This variable is required for generating secure tokens in web
     forms. It should have a secure, random value and it really has to be
     secret. For this reason, never add your `.env` file to a code repository.
   * `KERKO_ZOTERO_API_KEY`: The API key associated to the library on
     zotero.org. You may have to [create that
     key](https://www.zotero.org/settings/keys/new).
   * `KERKO_ZOTERO_LIBRARY_ID`: Your personal _userID_ for API calls, as given
     [on zotero.org](https://www.zotero.org/settings/keys) (you must be
     logged-in on zotero.org).
   * `KERKO_ZOTERO_LIBRARY_TYPE`: The type of library on zotero.org (either
     `'user'` for your main personal library, or `'group'` for a group library).

3. Synchronize data from zotero.org:

   ```bash
   flask kerko sync
   ```

   If you have a large bibliography and/or large file attachments, that command
   may take a while to complete (and there is no progress indicator). In
   production use, that command is usually added to the crontab file for regular
   execution.

   Note that Kerko provides a few Flask subcommands. To list them all:

   ```bash
   flask kerko --help
   ```

   To get details about a given subcommand:

   ```bash
   flask kerko SUBCOMMAND --help
   ```

4. Run EdTechHubLib using Flask's built-in server:

   ```bash
   flask run
   ```

5. With the server running, open http://localhost:5000/ in your browser to use
   the application.

Press CTRL+C from the terminal if you wish to stop the server.

Note that Flask's built-in server is **not suitable for production** as it
doesn't scale well, but is is perfectly adequate for development.

### Upgrading Python dependencies

There are two types of Python dependencies: (1) _run_ dependencies, which are
required to run the application; (2) _dev_ dependencies, which are required to
build the application. Those are specified in `requirements/run.in` and
`requirements/dev.in` respectively. To ensure reproducible results, exact
package versions are pinned into `requirements/run.txt` and
`requirements/dev.txt`.

With your virtual environment active, to upgrade a package PACKAGE to its latest
version and synchronize all installed dependencies:

```bash
pip-compile --upgrade-package PACKAGE --output-file requirements/run.in
pip-compile --upgrade-package PACKAGE --output-file requirements/dev.in
pip-sync requirements/dev.txt
```

After adequate testing, the updated `requirements/{dev,run}.{in,txt}` files can
be pushed to the repository for later deployment.

### Upgrading front-end dependencies

There are two types of front-end dependencies: (1) _asset_ dependencies, parts
of which are ingested by the build process and packaged into bundles, e.g.,
Bootstrap, jQuery; (2) _dev_ dependencies, which are tools required by the build
process, e.g., clean-css-cli, postcss-cli.

To upgrade an _asset_ dependency, manually edit the package's specification in
`frontendDependencies` section of `package.json`, then run the following
command:

```bash
npm install
```

To upgrade a _dev_ dependency PACKAGE to a version VERSION, run the following
command:

```bash
npm install PACKAGE@VERSION --save-dev
```

After a build (see the **Building the assets** section below) and adequate
testing, the updated `package.json` and `package-lock.json` files can be pushed
to the repository.

### Upgrading Kerko or changing Kerko's configuration

Kerko can be upgraded like regular Python packages (see **Upgrading Python
dependencies**). However, make sure to check [Kerko's changelog][Kerko_changelog].
The upgrade may require some changes to EdTechHubLib, or a rebuild of the search
index.

Similarly, some change to Kerko's configuration, especially changes to the
`KERKO_COMPOSER` variable in EdTechHubLib's `app/config.py`, may have an impact
on the structure of the search index. A rebuild of the search index may be
necessary after such change.

With your virtual environment active, to rebuild the search index:

```bash
flask kerko clean index
flask kerko sync
```

### Building the assets

If some front-end dependencies have been upgraded or if you have manually edited
a Sass stylesheet (from `app/static/src/scss/`), a rebuild of the assets is
required. From the application's directory (the one that contains `wsgi.py`),
and with your virtual environment active:

```bash
export PATH=`pwd`/node_modules/.bin:${PATH}
flask assets build
```

If you're happy with the results, build the minified assets for production use:

```bash
export ASSETS_DEBUG=False
flask assets build
```

Then push the updated files from `app/static/dist/` to the repository for later
deployment.

Note: Never manually edit the files in `app/static/dist/css/` or
`app/static/dist/js/`; any change will be overwritten by the build process.

## Deploying EdTechHubLib

There are two types of deployment: the initial installation or the deployment of
changes to an existing installation.

### Installing the application on Gandi

The following procedure has to be performed only once.

1. [Create](https://docs.gandi.net/en/simple_hosting/instance_management/create.html)
   a new Simple Hosting instance.

2. [Add SSH key(s)](https://docs.gandi.net/en/simple_hosting/connection/ssh_key.html#adding-a-public-ssh-key-to-your-instance)
   to the instance.

3. [Link domain](https://docs.gandi.net/en/simple_hosting/common_operations/link_to_domain.html)
   to the instance.

4. [Add Git remote](https://docs.gandi.net/en/simple_hosting/connection/git.html)
   to the local Git repository, e.g.:

   ```bash
   GIT_URL="ssh+git://{instance_id}@git.{datacenter_id}.gpaas.net"
   git remote add gandi $GIT_URL/default.git
   ```

   (Replace {instance_id} and {datacenter_id} with the appropriate values)

5. Deploy to the instance, e.g.:

   ```bash
   ssh $GIT_URL 'deploy default.git'
   ```

6. [Activate](https://docs.gandi.net/en/simple_hosting/connection/ssh.html) the
   Emergency Console (SSH)

7. SSH into the instance (requires instance password, SSH keys not supported):

   ```bash
   ssh {instance_id}@console.{datacenter_id}.gpaas.net
   ```

8. In the instance, create the `.env` file. See step 2 of **Installing the
   application locally** for details.

   TODO: .env path?

9.  Synchronize data from zotero.org:

    ```bash
    cd {home}
    {python_env}/bin/flask kerko sync
    ```

    TODO: home & flask paths?

11. In a browser, check that the site works.

12. Add scheduled task to `/srv/data/etc/cron/anacrontab`, e.g.:

    ```
    @daily 0 kerkosync cd {home} && {python_env}/bin/flask kerko sync
    ```

    TODO: home & flask paths?

### Deploying changes to the existing installation on Gandi

The following procedure is necessary to deploy changes to EdTechHubLib into
production.

1. Once all required changes have been implemented, built, and tested in the
   local environment, tag and push the new version to the repository, e.g.:

   ```bash
   git tag prod-`date -u +%Y%m%d-%H%M`
   git push gandi master && git push --tags
   ```

   If something goes wrong once in production, it will be easy to revert to the
   previously tagged version.

2. Deploy to the instance, e.g.:

   ```bash
   ssh $GIT_URL 'deploy default.git'
   ```

3. If changes require the search index to be rebuilt, SSH to the instance and
   run the following commands:

   TODO: home & flask paths?

   ```bash
   cd {home}
   {python_env}/bin/flask kerko clean index
   {python_env}/bin/flask kerko sync
   ```

[Flask]: https://pypi.org/project/Flask/
[Kerko]: https://github.com/whiskyechobravo/kerko
[Kerko_changelog]: https://github.com/whiskyechobravo/kerko/blob/master/CHANGELOG.md
[KerkoApp]: https://github.com/whiskyechobravo/kerkoapp
[Node.js]: https://nodejs.org/
[npm]: https://www.npmjs.com/
[Python]: https://www.python.org/
[virtualenv]: https://virtualenv.pypa.io/en/latest/
[Zotero]: https://www.zotero.org/
