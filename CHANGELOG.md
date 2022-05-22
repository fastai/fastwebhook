# Release notes

<!-- do not remove -->

## 0.0.15

### New Features

- [Enhancement] Clean up tweet body and @ mentions ([#44](https://github.com/fastai/fastwebhook/pull/44)), thanks to [@muellerzr](https://github.com/muellerzr)
- Use docments ([#37](https://github.com/fastai/fastwebhook/pull/37)), thanks to [@muellerzr](https://github.com/muellerzr)


## 0.0.13

### New Features

- Factor out `UnbufferedServer` base class ([#8](https://github.com/fastai/fastwebhook/issues/8))
- can specify hostname, etc params to `fastwebhook_install` ([#6](https://github.com/fastai/fastwebhook/issues/6))


## 0.0.12

### New Features

- add parameters to `fastwebhook_install`, and provide basic setup docs in README.md ([#7](https://github.com/fastai/fastwebhook/issues/7))

### Bugs squashed

- disable buffering so systemd journal works correctly


## 0.0.8

### New Features

- `fastwebhook_install` systemd installer ([#5](https://github.com/fastai/fastwebhook/issues/5))


## 0.0.6

### New Features

- new `debug` flag to skip actions ([#4](https://github.com/fastai/fastwebhook/issues/4))


## 0.0.4

### New Features

- optionally check source IP against github IPs ([#2](https://github.com/fastai/fastwebhook/issues/2))


## 0.0.1

### New Features

- Basic working webhook server with tweeting ([#1](https://github.com/fastai/fastwebhook/issues/1))

