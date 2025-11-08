==========
weixin
==========

.. autoclass:: python_plugins.weixin.wechat.Wechat

.. code-block:: python

   from python_plugins.weixin.wechat import Wechat

   class MyWechat(Wechat):
      def get_app(self) -> dict:
         return "<your app>"

   mywechat = MyWechat("name")
   mywechat.verify(query)
   mywechat.chat(query,content)

