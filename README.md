## Plugin updater plugin for mdmTerminal2
Автоматически обновляет плагины установленные из git.

## Установка
```
cd mdmTerminal2/src/plugins
git clone https://github.com/Aculeasis/mdmt2-plugin-updater
```
И перезапустить терминал.

## Настройка
Настройки хранятся в `mdmTerminal2/src/data/plugin_updater_config.json`, файл будет создан при первом запуске:
- **all**: Проверят обновления для всех плагинов. По умолчанию `false`.
- **broken**: Проверяет обновления только для "сломанных" плагинов. По умолчанию `false`.
- **deprecated**: Проверяет обновления только для устаревших плагинов. По умолчанию `true`.
- **restart**: Перезапустить терминал если плагины обновились. По умолчанию `true`.
