# api_on_DRF

## Описание проекта

В проекте сделаны:
* база данных;
* API на DRF.

## Причины по которым база данных и API были написаны выбранным образом

Данный проект является учебным. Было дано ТЗ в виде файла swagger.yaml (имеющегося в директрии), в котором прописаны 
список запросов и ответов, которые должен принимать и выдавать API соответствено.
К сожелению, в данном случае, сам сайт отправляет запросы отличные от тех, что представлены в swagger.yaml.
Для того, чтобы исправить недостатки, проявляющиеся в взаимодействии фронта и бэка, на отдельной ветке будут вносится
изменения в API, которая будет взаимодействовать с новой версией фронта.

База данных в данном проекте вактически подгонялась под фронт из-за чего получилась довольно грубой, хотя и рабочей.
В настоящее время не планируется переделывать БД, т.к. её изменение приведет к необходимости изменения всего фронта.
Также без изменения фронта API, взаимодействующая с нормальной БД, будет иметь слишком громоздкий вид.

