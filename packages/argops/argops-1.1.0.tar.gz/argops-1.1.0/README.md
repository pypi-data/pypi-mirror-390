# argops

A command-line interface for promoting Argocd applications between environments.

Features:

- Automate all the steps required to do a deployment
- Smart promote of value files between environments
- Dry-run option to see the changes.

## Installing

```bash
pipx install argops
```

It's recommended that you add to your ArgoCD `.gitignore` the `*-decrypted.yaml` string. This pattern will exclude these temporary files from being committed to your git repository. These files are created by `argops` during the decryption and encryption of sops secrets. Although `argops` cleans up these files after use, there's a possibility that they might be left behind if an error occurs during processing.

### Install the argocd commandline

- Follow [the official instructions](https://argo-cd.readthedocs.io/en/stable/cli_installation/)
- Configure the tool to use kubectl `argocd login --core`

### Install the gitea command line

- Follow [the official instructions](https://gitea.com/gitea/tea#installation)
- Use `tea login add` to connect to your gitea instance.

### Tweak your kubectl configuration

The `apply` command assumes that in your `kubectl` configuration you have context with the same name as the environments of argocd. It means that if you have a `staging` and `production` environments you should also have those in your contexts. If you use EKS it probably won't be the case and you'll need to edit them manually. To do so open the file `~/.kube/config` and under the `contexts` key: change the `name`:

```yaml
contexts:
  - context:
      cluster: arn:aws:eks:us-east-1:472857274883:cluster/production-cluster
      user: arn:aws:eks:us-east-1:472857274883:cluster/production-cluster
    name: production
  - context:
      cluster: arn:aws:eks:us-east-1:472857274883:cluster/staging-cluster
      user: arn:aws:eks:us-east-1:472857274883:cluster/staging-cluster
    name: staging
```

If you need to differentiate many production and staging clusters you can use the environment variable `ARGOPS_ENVIRONMENT_PREFIX`. If for example `ARGOPS_ENVIRONMENT_PREFIX=collectiveA` then your `kubectl` configuration may look like:

```yaml
contexts:
  - context:
      cluster: arn:aws:eks:us-east-1:472857274883:cluster/production-cluster
      user: arn:aws:eks:us-east-1:472857274883:cluster/production-cluster
    name: collectiveA-production
```

## Usage

There are currently two commands you can use:

- [`apply`](#apply)
- [`promote`](#promote)

### apply

`apply` will deploy the current local changes into the kubernetes cluster. It's meant to be run from the directory of the application you want to deploy.

If the changes are in the staging environment you can run:

```bash
argops apply
```

The tool will guide you through the required steps:

- Stage the changes you want to deploy
- Make the commit
- Push the changes to the git server
- Refresh the ArgoCD state
- Show the diff of the application
- Sync the changes
- Ask if you want to promote the changes in production

If you're on production, you'll need to use the environment flag `argops apply -e production`, this is a double check to make sure you are sure what you're doing.

The production workflow is almost the same as staging, but it will also open a pull request adding the application diff in the description of the pull and optionally merge it.

### promote

To use the tool, simply run it from your terminal on the directory where your environment directories are.

```bash
argops promote
```

By default the source directory is `staging` and the destination directory `production`. If you want to change them you can use the `--src-dir=<source directory>` and `--dest-dir=<destination directory>` flags. The `--dry-run` flag will show you what changes will it do without making them.

## Known issues

### Comments of promoted secrets are over the changed line

When you promote an environment specific values file, there are inline comments on the keys that have changed. However, sops doesn't support this format and adds the comment above the changed line. It's an upstream issue that is difficult to be addressed by us.

## Development

If you want to run the tool from source, make sure you have Python and all required packages installed. You can do this using:

```bash
git clone https://codeberg.org/lyz/argops
cd argops
make init
```

## Help

If you need help or want to report an issue, please see our [issue tracker](https://codeberg.org/lyz/argops/issues).

## License

GPLv3

## Authors

Lyz
