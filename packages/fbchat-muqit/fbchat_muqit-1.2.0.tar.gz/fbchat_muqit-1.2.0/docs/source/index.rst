
.. fbchat-muqit documentation master file

Welcome to fbchat-muqit
========================

**fbchat-muqit** is a powerful, modern Python library for interacting with Facebook Messenger. 
Built for speed, reliability, and ease of use.

----

Why fbchat-muqit?
-----------------

✨ **Modern & Async**
   Built with asyncio for high-performance concurrent operations

🚀 **Fast & Efficient**
   Optimized for speed - faster than previous fbchat implementations

🎯 **Type-Safe**
   Fully typed with comprehensive type hints for better IDE support

📦 **Easy to Use**
   Intuitive API design that feels natural and Pythonic

🔧 **Actively Maintained**
   Regular updates and improvements based on Facebook's API changes

----

Quick Start
-----------

Installation
~~~~~~~~~~~~

Install fbchat-muqit using pip:

.. code-block:: bash

   # Linux/MacOS
   python3 -m pip install -U fbchat-muqit

   # Windows
   py -3 -m pip install -U fbchat-muqit


Basic Usage
~~~~~~~~~~~

Here's a simple example to get you started:


.. warning:: Sending messages User to User on One to one chat is not supported anymore due to Messenger's **end-to-end encryption**. `see more <https://about.fb.com/news/2024/03/end-to-end-encryption-on-messenger-explained>`_.

.. code-block:: python

  from fbchat_muqit import Client, Message

  # Enter correct cookie file path
  client = Client(cookies_file_path="cookies.json")

  @client.event
  async def on_message(message: Message):
          
      # To avoid spam check if sender_id is client's id or not
      if message.sender_id != client.uid:

          text = f"You sent a message: {message.text}"

          await client.react(
                  reaction="❤️", 
                  message_id=message.id, 
                  thread_id=message.thread_id
                  )

          # reply to the message
          await client.send_message(
                  text=text, 
                  thread_id=message.thread_id, 
                  reply_to_message=message.id
                  )

  client.run()

----

Key Features
------------

Messaging
~~~~~~~~~
- Send text messages, files, images, videos, and more
- Reply to specific messages
- React with emojis
- Forward messages
- Unsend messages

Thread Management
~~~~~~~~~~~~~~~~~
- Create group chats
- Add/remove participants
- Change group names and photos
- Pin/unpin messages
- Set thread themes and emojis
- More

Real-time Events
~~~~~~~~~~~~~~~~
- Listen for incoming messages
- Handle typing indicators
- Track read receipts
- Monitor presence updates
- Receive notifications

User Operations
~~~~~~~~~~~~~~~
- Fetch user information
- Search for users
- Manage friend requests
- Block/unblock users
- Update profile information
- More

----

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   .. authentication

.. toctree::
   :maxdepth: 2
   :caption: User Guides
     
   guides/handling-events
   .. guides/sending-messages
   .. guides/attachments
   .. guides/thread-management
   .. guides/error-handling

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/models/index
   api/facebook-client
   api/messenger-client
   api/events


.. toctree::
   :maxdepth: 1
   :caption: Examples

   .. examples/basic-bot
   .. examples/event-listener
   .. examples/file-sharing
   .. examples/group-management

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   .. changelog
   .. contributing
   .. license

----

Support & Community
-------------------

- **GitHub Issues**: Report bugs or request features
- **Email**: -
- **Facebook**: `MuQiT.dev <https://www.facebook.com/MuQiT.dev>`_
- **License**: GPL-V3.0

----

Project Information
-------------------

:Version: |version|
:Author: Muhammad MuQiT
:License: GPL-V3.0
:Copyright: Copyright 2024-2025 by Muhammad MuQiT

----

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
