<p align="center"><img src="Logo.png" alt="Логотип Newgramm" width="256"></p>

# Newgramm
Newgramm - российская социальная сеть с привычным интерфейсом и широкими возможностями. В России Instagram заблокировали, но не стоит волноваться, 
ведь есть Newgramm. Идея была в том, чтобы создать привычное для пользователей приложение, выполняющее функцию Instagram. И у нас это получилось! Похожий интерфейс, привычные вкладки и профили пользователей с фотографиями.


# Сайт

Сайт - https://newgramm.pythonanywhere.com/
> Если вы столкнулись с какой либо ошибкой, пожалуйста создайте [issue](https://github.com/Nytrock/Newgramm/issues).
> 
> Предложения по улучшению сайта просьба писать на почту newgrammowner@gmail.com

# Структура сайта

## Регистация и вход
При первом входе на сайт вам сразу же предложат зарегистрироваться. Процесс регистрации состоит из заполнения таких полей как: логин, описание, фото профиля, возраст, почта, пароль, тэги. Под тэгами подразумеваются темы, наиболее близкие конкретно вам и на основе которых в будущем будут создаваться рекомендации. Для входа необходимо ввести почту и пароль. Также, если вы хотите остаться в системе после ухода с сайта, необходимо это указать при входе.

## Профиль пользователя
В профиле пользователя находится вся иформация о нём, а именно: аватарка, описание профиля, количество постов, подписок, подписчиков и список всех постов.
Вы можете просмотреть списки всех пользователей, которые подписаны на профиль или пользователей, на которых подписан владелец профиля. Вы также можете сортировать эти списки. В списке постов вы можете выбрать любой пост для его подробного просмотра, а далее удобно листать список постов, не выходя со страницы поста. Если вы находитесь в своём профиле, вы можете изменить информацию профиля, удалить профиль или выйти из профиля. Если вы находитесь в профиле другого пользовтеля, то вы можете
либо подписаться на него, либо от него отписаться.

## Лента
Отображение всех постов пользователей, на которых вы подписаны. Вы можете легко отписаться от пользователя прямо в ленте, посетить его профиль. Также можно сортировать все посты в ленте по популярности и дате выкладывания, посмотреть подробную информацию о посте перейдя на его страницу, а после этого удобно листать ленту, не выходя с этой страницы.

## Рекомендации
Отображение постов, которые будут вам интересны. Список постов составляется на основе тем, указанных в вашем профиле. Также как и в ленте вы можете подписаться на пользователя, посетить его профиль, перейти на страницу поста, листать рекомендации не выходя сос страницы поста.

## Поиск
Позволяет найти любого пользователя по его почте или логину. Можно сразу подписаться на найденного пользователя.

## Создание поста
Для создания поста нужно заполнть несколько полей: описание поста, его тэги (то бишь темы), фотография поста. Ещё нужно указать, можно ли будет оставлять комментарии постом.

## Страница поста
Отображение фотографии поста, его описания, даты выкладывания, аватарки и логина создателя поста, количества лайков и комментариев, если они включены. Если вы смотрите собственный пост, то можете его изменить или удалить, но не лайкнуть (самолайкерство это плохо). Если же вы смотрите пост другого пользователя, то можете подписаться на него или отписаться от него, поставить лайк посту. При включенных комментариях можно оставить свой. Все комментарии можно сортировать по новизне, а коммментарии, которые были написаны вами, вы можете только удалить, не изменить.

# API
На Newgramm также есть API. На самом [сайте](https://newgramm.pythonanywhere.com) после инцидента с дудосом через API можно только получить информацию об одном или нескольких  постах, пользователях и комментариях. Локальная же версия имеет расширенное API, с помощью которого можно также создавать и удалять посты, комментарии и пользователей. Подробнее о том, как правильно пользоваться API, написано [здесь](https://github.com/Nytrock/Newgramm/wiki/API-documentation).

# Инструкция по запуску на локальной машине

 - Клонировать репозиторий

	```shell
	git clone https://github.com/Nytrock/Newgramm.git
	```

 - Установить зависимости с помощью requirements.txt
	```shell
	pip install -r requirements.txt
	```
  
 - Для полноценной работы регистрации поле базы данных "theme" необходимо заполнить данными о тегах. 
 Приложение было разработано на flask, из-за чего не может предложить удобной работы с базой данных без участия сторонних программ.
 В качестве одной из программ, которая может помочь выйти из этой проблемы, рекомендуем попробовать [SQLiteStudio](https://sqlitestudio.pl/).
 
 - Запустите файл `flask_app.py`
 - Перейдите по ссылке `http://127.0.0.1:8000`
