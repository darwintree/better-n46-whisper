# README

`better-n46-whisper` 是一个基于 [whisperX](https://github.com/m-bain/whisperX) 的工具项目，旨在为跨语种字幕制作等音视频处理工作提供预处理支持。本项目的目标是实现停止维护的[N46Whisper](https://github.com/Ayanaminn/N46Whisper)功能的超集，在其功能基础上包含以下feature：

- [ ] run in local env or colab
- [x] bunch translation
  - [x] better context
  - [ ] ~~and less token consumption~~
- [ ] different LLM translation backend
    - [ ] Remote: ChatGLM
    - [ ] Local: ChatGLM, Baichuan
- [x] speaker tag support
    - [x] better context for LLM input
    - [x] different subtitle output style for different user
- [ ] GUI(low priority)
- [ ] async translation request
- [ ] align translation using LLM
- [ ] support karaoke
  - [ ] raw: uvr5 preprocess
  - [ ] lrc

本项目正在前期开发中。

## TODOs other than desired features

- [ ] better speaker split
- [ ] better line width style
- [ ] contribute code back to whisperX
- [ ] language support other than Japanese

## Initial Roadmap

1. WhisperX and LLM support with practical documentation. Runnable in local env or within Colab
2. Inherit N46Whisper ipynb features
3. async LLM translation
4. more remote LLM support
5. local LLM support

