---

# cg_api

_cg_api_ is a wrapper around the [CloudGuard](https://www.checkpoint.com/cloudguard) API.

The purpose is to reduce boilerplate, and encourage interactive exploration.

Credentials are loaded from environment variables or from a configuration file.

_cg_api_ is loosely inspired by aws-cli / boto3, the configuration file has
a similar format:

```
[default]
CLOUDGUARD_URL=
CLOUDGUARD_ID=
CLOUDGUARD_SECRET=
```

## Installation

```
pip install git+https://github.com/jzr/cg-api
```

## Usage

```python
import cg_api

session = cg_api.Session()
print(session.whoami())

demo_session = cg_api.Session(profile_name="demo")
print(session.get("user/me"))
```

## Configuration

The default load order is:

- `EnvironmentProvider`
- `FileConfigProvider`

### From environment: `EnvironmentProvider`

Requires three environment variables defined.
```
CLOUDGUARD_URL=
CLOUDGUARD_ID=
CLOUDGUARD_SECRET=
```

### From file: `FileConfigProvider`

The default file is `~/.cloudguard/credentials`.
This can be changed by setting `CLOUDGUARD_SHARED_CREDENTIALS_FILE`.

This provider requires at least one profile to be configured.
Setting the `CLOUDGUARD_PROFILE` environment variable will change the selected profile.

Secondary profiles can omit `CLOUDGUARD_URL` as long as it is configured in the _default_ section.

```
[default]
CLOUDGUARD_URL=
CLOUDGUARD_ID=
CLOUDGUARD_SECRET=

[readonly]
CLOUDGUARD_ID=
CLOUDGUARD_SECRET=
```

### From random: `RandomConfigProvider`

Purely for entertainment purposes.
Will generate random URL and credentials.
