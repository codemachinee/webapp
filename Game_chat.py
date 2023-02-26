import asyncio

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async

MAX_MESSAGES_CNT = 200  # максимальное количество хранящихся сообщений

chat_msgs = []  # список храннящий историю сообщений
online_users = set()  # множество хранящее онлайн пользователей
true_password = None


# def t(eng, chinese):
#   """return English or Chinese text according to the user's browser language"""
#  return chinese if 'zh' in session_info.user_language else eng


async def refresh_msg(my_name):
    """send new message to current session"""
    global chat_msgs
    last_idx = len(chat_msgs)
    while True:
        await asyncio.sleep(0.5)
        for m in chat_msgs[last_idx:]:
            if m[0] != my_name:  # only refresh message that not sent by current user
                put_markdown('`%s`: %s' % m, sanitize=True, scope='msg-box')

        # remove expired message
        if len(chat_msgs) > MAX_MESSAGES_CNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)


async def main():
    global chat_msgs, true_password

    put_markdown("#🏆Добро пожаловать в игровой чат!🏆\nДанный чат разработан как вспомогательный инструмент"
                 " для скорейшего достижения прекрасного настроения\n"
                 "\n created by hlapps")

    put_scrollable(put_scope('msg-box'), height=300, keep_bottom=True)  # поле сообщений
    nickname = await input("Войти в чат", required=True, placeholder='Введите Ваше имя',  # поле ввода имени
                           validate=lambda n: 'Такое имя уже используется' if n in online_users or n == '📢' else None)
    if true_password is None:
        if nickname in ('sexmashine', 'admin', 'сексмашина'):
            password = await input('Введите пароль', required=False, type='password', placeholder='задайте пароль '
                                                                                                  'секретного чата')
            true_password = password
        else:
            password = await input('Введите пароль', required=False, type='password',
                                   placeholder='пароль секретного чата, '
                                               'если он есть')
        online_users.add(nickname)
        chat_msgs.append(('📢', '`%s` вошел(а) в чат. %s пользователя онлайн' % (nickname, len(online_users))))
        put_markdown('`📢`: `%s` вошел(а) в чат. %s пользователя онлайн' % (nickname, len(online_users)),
                     sanitize=True,
                     scope='msg-box')
    else:
        password = await input('Введите пароль', required=False, type='password', placeholder='пароль секретного чата, '
                                                                                              'если он есть',
                               validate=lambda m: 'Неверный пароль' if m != true_password else None)
        online_users.add(nickname)  # игрок добавлен в онлайн список
        chat_msgs.append(('📢', '`%s` вошел(а) в чат. %s пользователя онлайн' % (nickname, len(online_users))))
        put_markdown('`📢`: `%s` вошел(а) в чат. %s пользователя онлайн' % (nickname, len(online_users)), sanitize=True,
                     scope='msg-box')

    @defer_call
    def on_close():
        online_users.remove(nickname)
        chat_msgs.append(('📢', '`%s` покинул(а) чат. %s пользователя онлайн' % (nickname, len(online_users))))

    refresh_task = run_async(refresh_msg(nickname))

    while True:
        data = await input_group('Отправить сообщение', [
            textarea(name='msg', help_text='Введите текст сообщения'),
            #input(name='msg'),
            actions(name='cmd', buttons=['Отправить',
                                         {'label': 'Выход', 'type': 'cancel'}])
        ], validate=lambda d: ('msg', 'Пустое сообщение') if d['cmd'] == 'Отправить' and not d[
            'msg'] else None)
        if data is None:
            break
        put_markdown('`%s`: %s' % (nickname, data['msg']), sanitize=True, scope='msg-box')
        chat_msgs.append((nickname, data['msg']))

    refresh_task.close()
    toast("Вы покинули чат")


if __name__ == '__main__':
    start_server(main, debug=True, port=80, remote_access=True)
