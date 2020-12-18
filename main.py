import os
import sys
import logging
from io import BytesIO
from PIL import ImageOps
from PIL import Image
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from matplotlib import pyplot

import algorithms

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
current_module_name = sys.modules[__name__]

current_image = {}
is_ready_to_upload = set()
TEMP_FILE_PATH = 'data/outfile.png'
TOKEN_FILE_PATH = 'data/token/token.txt'
PROXY_FILE_PATH = 'data/proxy/proxy.txt'
EXAMPLES_DIR_PATH = 'data/examples/'


def get_image(current_image):
    image_bytes = BytesIO(current_image.download_as_bytearray())
    image_bytes.seek(0)
    image = Image.open(image_bytes)
    return image


def opt_binary_1(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        image = ImageOps.invert(image)
        image.save(TEMP_FILE_PATH)
        query.edit_message_text(text="Inverted image")
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
    else:
        query.edit_message_text(text="Nothing to work with")


def opt_binary_2(query, bot, message):
    global current_image

    if message.chat.id in current_image:

        keyboard = [
            [
                InlineKeyboardButton("Diamond 3x3", callback_data='_binary_21'),
                InlineKeyboardButton("Diamond 5x5", callback_data='_binary_22'),
            ],
            [
                InlineKeyboardButton("Disk 3x3", callback_data='_binary_23'),
                InlineKeyboardButton("Disk 5x5", callback_data='_binary_24'),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text='Make sure you have uploaded binary image, otherwise skeletization result may be unexpected. '
                 + 'Please choose structuring element', reply_markup=reply_markup)

    else:
        query.edit_message_text(text="Nothing to work with")


def opt_binary_2x(query, bot, message, str_name, str_shape):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        skeletonized_img, restored_img, n_total = algorithms.morphological_skeleton.skeletonize_n_restore(image,
                                                                                                          str_name,
                                                                                                          str_shape)
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


def opt_binary_21(query, bot, message):
    opt_binary_2x(query, bot, message, 'diamond', 3)


def opt_binary_22(query, bot, message):
    opt_binary_2x(query, bot, message, 'diamond', 5)


def opt_binary_23(query, bot, message):
    opt_binary_2x(query, bot, message, 'disk', 3)


def opt_binary_24(query, bot, message):
    opt_binary_2x(query, bot, message, 'disk', 5)


def opt_binary_3(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        skeletonized_img, n_total = algorithms.skeletonize(image)
        query.edit_message_text(
            text="Image skeletonized with thinning")
        pyplot.imsave(TEMP_FILE_PATH, skeletonized_img, cmap=pyplot.cm.gray)
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
        bot.send_message(message.chat.id, text='Iterations number: {}'.format(n_total))
    else:
        query.edit_message_text(text="Nothing to work with")


def opt_binary_4(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        hull_img, n_total = algorithms.get_convex_hull(image)
        query.edit_message_text(
            text="Convex hull of image")
        pyplot.imsave(TEMP_FILE_PATH, hull_img, cmap=pyplot.cm.gray)
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
        bot.send_message(message.chat.id, text='Iterations number: {}'.format(n_total))
    else:
        query.edit_message_text(text="Nothing to work with")


def opt_binary_5(query, bot, message):
    global current_image

    if message.chat.id in current_image:

        keyboard = [
            [
                InlineKeyboardButton("Square 3x3", callback_data='_binary_51'),
                InlineKeyboardButton("Square 5x5", callback_data='_binary_52'),
                InlineKeyboardButton("Square 7x7", callback_data='_binary_53'),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text='Make sure you have uploaded binary image, otherwise filtration result may be unexpected. '
                 + 'Please choose frame element', reply_markup=reply_markup)

    else:
        query.edit_message_text(text="Nothing to work with")


def opt_binary_5x(query, bot, message, f_size):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        filtered_img = algorithms.filter_binary_image(image, f_size)
        query.edit_message_text(
            text="Image filtered with square {}x{}".format(f_size, f_size))
        pyplot.imsave(TEMP_FILE_PATH, filtered_img, cmap=pyplot.cm.gray)
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
    else:
        query.edit_message_text(text="Nothing to work with")


def opt_binary_51(query, bot, message):
    opt_binary_5x(query, bot, message, 3)


def opt_binary_52(query, bot, message):
    opt_binary_5x(query, bot, message, 5)


def opt_binary_53(query, bot, message):
    opt_binary_5x(query, bot, message, 7)


def opt_binary(query, bot, message):
    global current_image

    if message.chat.id in current_image:

        keyboard = [
            [
                InlineKeyboardButton("Invert image", callback_data='_binary_1'),
            ],
            [
                InlineKeyboardButton("Skeletonize image", callback_data='_binary_2'),
            ],
            [
                InlineKeyboardButton("Skeletonize image with thinning", callback_data='_binary_3'),
            ],
            [
                InlineKeyboardButton("Get convex hull with thickening", callback_data='_binary_4'),
            ],
            [
                InlineKeyboardButton("Stub", callback_data='_binary_5'),
            ],
            [
                InlineKeyboardButton("Filter image", callback_data='_binary_6'),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text='Make sure you have uploaded binary image, otherwise result may be unexpected.',
            reply_markup=reply_markup)

    else:
        query.edit_message_text(text="Nothing to work with")


def opt_grayscale_2(query, bot, message):
    global current_image

    if message.chat.id in current_image:

        keyboard = [
            [
                InlineKeyboardButton("Square 3x3", callback_data='_grayscale_21'),
                InlineKeyboardButton("Square 5x5", callback_data='_grayscale_22'),
                InlineKeyboardButton("Square 7x7", callback_data='_grayscale_23'),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text='Make sure you have uploaded grayscale image, otherwise filtration result may be unexpected. '
                 + 'Please choose frame element', reply_markup=reply_markup)

    else:
        query.edit_message_text(text="Nothing to work with")


def opt_grayscale_2x(query, bot, message, f_size):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        filtered_img = algorithms.filter_grayscale_image(image, f_size)
        query.edit_message_text(
            text="Image filtered with square {}x{}".format(f_size, f_size))
        pyplot.imsave(TEMP_FILE_PATH, filtered_img, cmap=pyplot.cm.gray)
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
    else:
        query.edit_message_text(text="Nothing to work with")


def opt_grayscale_21(query, bot, message):
    opt_grayscale_2x(query, bot, message, 3)


def opt_grayscale_22(query, bot, message):
    opt_grayscale_2x(query, bot, message, 5)


def opt_grayscale_23(query, bot, message):
    opt_grayscale_2x(query, bot, message, 7)


def opt_grayscale(query, bot, message):
    global current_image

    if message.chat.id in current_image:

        keyboard = [
            [
                InlineKeyboardButton("Stub", callback_data='_grayscale_1'),
            ],
            [
                InlineKeyboardButton("Filter image", callback_data='_grayscale_2'),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text='Make sure you have uploaded grayscale image, otherwise result may be unexpected.',
            reply_markup=reply_markup)

    else:
        query.edit_message_text(text="Nothing to work with")


def opt_colored_1(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        image = ImageOps.grayscale(image)
        image.save(TEMP_FILE_PATH)
        query.edit_message_text(text="Grayscale image")
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
    else:
        query.edit_message_text(text="Nothing to work with")


def opt_colored_2(query, bot, message):
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


def opt_colored(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        keyboard = [
            [
                InlineKeyboardButton("To grayscale", callback_data='_colored_1')
            ],
            [
                InlineKeyboardButton("To binary", callback_data='_colored_2')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text='Choose option:',
            reply_markup=reply_markup)
    else:
        query.edit_message_text(text="Nothing to work with")


def opt_common_1(query, bot, message):
    global current_image
    global is_ready_to_upload

    query.edit_message_text(text="Upload image")
    is_ready_to_upload.add(message.chat.id)


def opt_common_2(query, bot, message):
    global current_image

    if message.chat.id in current_image:
        query.edit_message_text(text="Processing...")
        image = get_image(current_image[message.chat.id])
        image.save(TEMP_FILE_PATH)
        query.edit_message_text(text="Here is your image")
        bot.send_photo(message.chat.id, photo=open(TEMP_FILE_PATH, 'rb'))
    else:
        query.edit_message_text(text="Nothing to show")


def opt_common_3(query, bot, message):
    query.edit_message_text(text="Here are some image examples")
    for filename in os.listdir(EXAMPLES_DIR_PATH):
        bot.send_message(message.chat.id, filename)
        bot.send_photo(message.chat.id, photo=open(os.path.join(EXAMPLES_DIR_PATH, filename), 'rb'))


def start(update: Update, context: CallbackContext) -> None:
    bot = update.message.bot
    message = update.message
    bot.send_message(message.chat.id, "Hi! Call /menu to go on")


def menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        # [
        #     InlineKeyboardButton("To grayscale", callback_data='1'),
        #     InlineKeyboardButton("To binary", callback_data='2'),
        # ],
        # [
        #     InlineKeyboardButton("Invert image", callback_data='3'),
        #     InlineKeyboardButton("Stub", callback_data='4'),
        # ],
        # [
        #     InlineKeyboardButton("Skeletonize image", callback_data='5'),
        # ],
        # [
        #     InlineKeyboardButton("Skeletonize image with thinning", callback_data='6'),
        # ],
        # [
        #     InlineKeyboardButton("Get convex hull with thickening", callback_data='7'),
        # ],
        # [
        #     InlineKeyboardButton("Stub", callback_data='8'),
        # ],
        # [
        #     InlineKeyboardButton("Filter grayscale image", callback_data='9'),
        #     InlineKeyboardButton("Filter binary image", callback_data='10')
        # ],
        [InlineKeyboardButton("Binary", callback_data='_binary')],
        [InlineKeyboardButton("Grayscale", callback_data='_grayscale')],
        [InlineKeyboardButton("Colored", callback_data='_colored')],
        [InlineKeyboardButton("Upload image", callback_data='_common_1')],
        [InlineKeyboardButton("Show current image", callback_data='_common_2')],
        [InlineKeyboardButton("Show image examples", callback_data='_common_3')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    bot = query.bot
    message = query.message

    option = query.data

    query.answer()

    getattr(current_module_name, 'opt' + str(option))(query, bot, message)

    # if option in options:
    #     options[option](query, bot, message)


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Use /start to test this bot.")


def image_handler(update: Update, context: CallbackContext) -> None:
    global current_image
    global is_ready_to_upload
    bot = update.message.bot
    message = update.message

    if message.chat.id in is_ready_to_upload:
        current_image[message.chat.id] = bot.getFile(update.message.photo[-1].file_id)
        bot.send_message(message.chat.id, 'Image is successfully uploaded')
        is_ready_to_upload.remove(message.chat.id)

    else:
        bot.send_message(message.chat.id, 'Please choose \'Upload image\' button from /menu to upload image')


def main():
    with open(TOKEN_FILE_PATH, 'r') as file:
        token = file.read()

    with open(PROXY_FILE_PATH, 'r') as file:
        proxy = file.read()

    # request_kwargs = {
    #     'proxy_url': 'http://'+proxy,
    # }
    #
    # updater = Updater(token, use_context=True, request_kwargs=request_kwargs)

    updater = Updater(token, use_context=True, )

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
