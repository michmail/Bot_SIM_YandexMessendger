# -*- coding: utf-8 -*-
from chats import dp
from inline import dp
from schedules import scheduler

from Utilities.Utilities import main
from Utilities.Telegram import executor

# Inner launch
if __name__ == '__main__':
    scheduler.start()
    main(executor.start_polling, dispatcher=dp)
