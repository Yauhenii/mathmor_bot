import os
import logging
from io import BytesIO
import PIL.ImageOps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

from matplotlib import pyplot

from algorithms import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

current_image = {}
is_ready_to_upload = False
TEMP_FILE_PATH = 'data/outfile.png'
TOKEN_FILE_PATH = 'data/token/token.txt'
EXAMPLES_DIR_PATH = 'data/examples/'


def get_image(current_image):
    image_bytes = BytesIO(current_image.download_as_bytearray())
    image_bytes.seek(0)
    image = Image.open(image_bytes)
    return image


def opt1(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        image = image.convert('LA')
        image.save(TEMP_FILE_PATH)
        query.edit_message_text(text="Grayscale image")
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
    else:
        query.edit_message_text(text="Nothing to work with")


def opt2(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        threshold = 128
        image = image.convert('L').point(lambda x: 255 if x > threshold else 0, mode='1')
        image.save(TEMP_FILE_PATH)
        query.edit_message_text(text="Binary image")
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
    else:
        query.edit_message_text(text="Nothing to work with")


def opt3(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        image = PIL.ImageOps.invert(image)
        image.save(TEMP_FILE_PATH)
        query.edit_message_text(text="Inverted image")
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
    else:
        query.edit_message_text(text="Nothing to work with")


def opt4(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Stub")
    else:
        query.edit_message_text(text="Nothing to work with. Stub")


def opt5(query, bot, message):
    global current_image

    if message.chat.id in current_image:

        keyboard = [
            [
                InlineKeyboardButton("Diamond 3x3", callback_data='51'),
                InlineKeyboardButton("Diamond 5x5", callback_data='52'),
            ],
            [
                InlineKeyboardButton("Disk 3x3", callback_data='53'),
                InlineKeyboardButton("Disk 5x5", callback_data='54'),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text='Make sure you have uploaded binary image, otherwise skeletization result may be unexpected. '
                 + 'Please choose structuring element', reply_markup=reply_markup)

    else:
        query.edit_message_text(text="Nothing to work with")


def opt5x(query, bot, message, str_name, str_shape):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        skeletonized_img, restored_img, n_total = skeletonize_n_restore(image, str_name, str_shape)
        query.edit_message_text(
            text="Image skeletonized with {} {}x{}".format(str_name, str_shape, str_shape))
        pyplot.imsave(TEMP_FILE_PATH, skeletonized_img, cmap=pyplot.cm.gray)
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
        pyplot.imsave(TEMP_FILE_PATH, restored_img, cmap=pyplot.cm.gray)
        bot.send_message(message.chat.id, text='Restored image')
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
        bot.send_message(message.chat.id, text='Erosion or dilation number: {}'.format(n_total))
    else:
        query.edit_message_text(text="Nothing to work with")


def opt51(query, bot, message):
    opt5x(query, bot, message, 'diamond', 3)


def opt52(query, bot, message):
    opt5x(query, bot, message, 'diamond', 5)


def opt53(query, bot, message):
    opt5x(query, bot, message, 'disk', 3)


def opt54(query, bot, message):
    opt5x(query, bot, message, 'disk', 5)


def opt11(query, bot, message):
    global current_image
    global is_ready_to_upload

    query.edit_message_text(text="Upload image")
    is_ready_to_upload = True


def opt12(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        image.save(TEMP_FILE_PATH)
        query.edit_message_text(text="Here is your image")
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
    else:
        query.edit_message_text(text="Nothing to show")


def opt13(query, bot, message):
    query.edit_message_text(text="Here are some image examples")
    for filename in os.listdir(EXAMPLES_DIR_PATH):
        bot.send_message(message.chat.id, filename)
        bot.send_photo(message.chat.id, photo=open(os.path.join(EXAMPLES_DIR_PATH, filename), 'rb'))


options = {
    '1': opt1,
    '2': opt2,
    '3': opt3,
    '4': opt4,
    '5': opt5,
    '11': opt11,
    '12': opt12,
    '13': opt13,
    '51': opt51,
    '52': opt52,
    '53': opt53,
    '54': opt54
}


def start(update: Update, context: CallbackContext) -> None:
    bot = update.message.bot
    message = update.message

    bot.send_message(message.chat.id, "Hi! Call /menu to go on")


def menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("To grayscale", callback_data='1'),
            InlineKeyboardButton("To binary", callback_data='2'),
        ],
        [
            InlineKeyboardButton("Invert image", callback_data='3'),
            InlineKeyboardButton("Stub", callback_data='4'),
        ],
        [
            InlineKeyboardButton("Skeletonize image", callback_data='5'),
        ],
        [InlineKeyboardButton("Upload image", callback_data='11')],
        [InlineKeyboardButton("Show current image", callback_data='12')],
        [InlineKeyboardButton("Show image examples", callback_data='13')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    global options

    query = update.callback_query
    bot = query.bot
    message = query.message

    option = query.data

    query.answer()

    if option in options:
        options[option](query, bot, message)


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Use /start to test this bot.")


def image_handler(update: Update, context: CallbackContext) -> None:
    global current_image
    global is_ready_to_upload
    bot = update.message.bot
    message = update.message

    if is_ready_to_upload:
        current_image[message.chat.id] = bot.getFile(update.message.photo[-1].file_id)
        bot.send_message(message.chat.id, 'Image is successfully uploaded')
        is_ready_to_upload = False

    else:
        bot.send_message(message.chat.id, 'Please choose \'Upload image\' button from /menu to upload image')


def main():
    with open(TOKEN_FILE_PATH, 'r') as file:
        token = file.read()
    updater = Updater(token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('menu', menu))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
