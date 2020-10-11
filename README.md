# fastwebhook
> A simple GitHub webhook server.


At this stage, this is only able to send tweets on software releases. It's very early stage still. You'll need to set up a webhook on GitHub.

## Install

First install the package:

`pip install fastwebhook`

Then create an file called `twitter.ini` containing:

```
gh_secret: 
consumer_key: 
consumer_secret: 
access_token: 
access_token_secret: 
```

`gh_secret` is the webhook secret you set in GitHub. The remaining are your twitter API keys.

## How to use

Run `fastwebhook` to run the web server. Pass `--help` for info about optional arguments. Either run this from the same directory that contains your `twitter.ini`, or else pass `--inifile` along with the full path to your ini file.

### Systemd service

The following commands should all be run as root (i.e. prepend `sudo` to the commands).

To install it as a systemd service (which is probably what you want), run `fastwebhook_install`. Pass `--help` for info about optional arguments, which will be passed to `fastwebhook` by the service.

After the service is installed, run `systemctl start fastwebhook` to start it, `systemctl status fastwebhook` to check it, and `systemctl stop fastwebhook` to stop it. Run `systemctl enable fastwebhook` to have it start automatically on boot. Run `journalctl -eu fastwebhook`
