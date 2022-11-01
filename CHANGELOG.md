# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## 2022-08-31
### Changed
- Rename project


## 2022-08-02
### Fixed
- Situation was fixed: Data collection will hung if stream doesn't produce any events after restart.
Why doesn't steam produce any events? It's highly likely Tinkoff API bug. 


## 2022-07-04
### Added
- Added watcher to handle any hangs due trade session. Sometimes market stream can hang while trade session.
### Changed
- The tool has been rewritten to handle trade schedule and now is working as service and handles trade schedule by self.     


## 2022-06-29
### Added
- Added awaiting to start market stream if the tool has been started before start trading session.
Sometimes market stream can hang if you start it before start trading session.
