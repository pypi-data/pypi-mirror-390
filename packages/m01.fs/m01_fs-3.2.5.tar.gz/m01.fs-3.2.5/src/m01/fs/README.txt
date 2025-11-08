======
README
======

This package provides a file and storage implementation for zope3 without
using the mongodb GridFS. As you probably know, the GridFS should not get used
for small binar data because it will double the number of queries. This package
will provide a simple file object which stores the file meta and chunk data in
one mongodb document (object).

NOTE: We also provide an m01.grid package which supports th GridFS
implementation with a similar API. The m01.grid is recommended if you need to
store larger data then the mongodb can store for one doucment.


How we process file upload
--------------------------

This description defines how a file upload will get processd in some raw
steps. It defines some internal part we use for processing an input stream
but it doesn't really explain how we implemented the file storage pattern.

The browser defins a form with a file upload input field:

  - client starts file upload

The file upload will get sent to the server:

  - create request

  - read input stream

  - process input stream

    - define a cgi parser (p01.cgi.parser.parseFormData)

    - parse input stream with cgi parser

      - write file upload part in tmp file

      - wrap file upload part from input stream with FileUpload

    - store FileUpload instance in request.form with the form input field
      name as key

The file upload get processed from the request by using z3c.form components:

  - z3c.form defines a widget

  - z3c.widget reads the FileUpload from the request

  - z3c.form data converter returns the plain FileUpload

  - z3c.form data manager stores the FileUpload as attribute value

Each file item provides an fileUpload property (attribute) which is responsible
to process the given FileUpload object. The defualt built-in fileUpload
property does the following:

  - get a FileWriter

The FileWrite knows how to write the given FileUpload tmp file to mongodb.


setup
-----

  >>> import re
  >>> import sys
  >>> from pprint import pprint
  >>> from pymongo import ASCENDING
  >>> import transaction
  >>> import m01.mongo.testing
  >>> import m01.fs.testing

  >>> try:
  ...     ignored = unicode # p01.checker.silence
  ... except Exception as e:
  ...     unicode = str # p01.checker.silence

Also define a normalizer:

  >>> patterns = [
  ...    (re.compile("u'__name__':"), r"'__name__':"),
  ...    (re.compile("u'_id':"), r"'_id':"),
  ...    (re.compile("u'_pid':"), r"'_pid':"),
  ...    (re.compile("u'_type':"), r"'_type':"),
  ...    (re.compile("u'_version':"), r"'_version':"),
  ...    (re.compile("u'contentType':"), r"'contentType':"),
  ...    (re.compile("u'created':"), r"'created':"),
  ...    (re.compile("u'data':"), r"'data':"),
  ...    (re.compile("u'description':"), r"'description':"),
  ...    (re.compile("u'encoding':"), r"'encoding':"),
  ...    (re.compile("u'filename':"), r"'filename':"),
  ...    (re.compile("u'md5':"), r"'md5':"),
  ...    (re.compile("u'modified':"), r"'modified':"),
  ...    (re.compile("u'removed':"), r"'removed':"),
  ...    (re.compile("u'size':"), r"'size':"),
  ...    (re.compile("u'title':"), r"'title':"),
  ...    (re.compile("u'uploadDate':"), r"'uploadDate':"),
  ...    (re.compile(r"'__name__': u'"), r"'__name__': '"),
  ...    (re.compile(r"'__name__': '[a-zA-Z0-9]+'"), r"'__name__': '...'"),
  ...    (re.compile(r"ObjectId\('[a-zA-Z0-9]+'\)"), r"ObjectId('...')"),
  ...    (re.compile(r"datetime.datetime\([a-zA-Z0-9, ]+tzinfo=<bson.tz_util.FixedOffset[a-zA-Z0-9 ]+>\)"),
  ...                "datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>)"),
  ...    (re.compile(r"datetime.datetime\([a-zA-Z0-9, ]+tzinfo=[a-zA-Z0-9>]+\)"),
  ...                "datetime(..., tzinfo= ...)"),
  ...    (re.compile(r"datetime\([a-z0-9, ]+\)"), "datetime(...)"),
  ...    (re.compile(r"object at 0x[a-zA-Z0-9]+"), "object at ..."),
  ...    (re.compile(r"'_type': u'"), r"'_type': '"),
  ...    (re.compile(r"'contentType': u'"), r"'contentType': '"),
  ...    (re.compile(r"'description': u'"), r"'description': '"),
  ...    (re.compile(r"'title': u'"), r"'title': '"),
  ...    (re.compile(r"'title': u'"), r"'title': '"),
  ...    (re.compile(r"'filename': u'"), r"'filename': '"),
  ...    (re.compile(r"'md5': u'"), r"'md5': '"),
  ...    #(re.compile(r"'md5': '[a-zA-Z0-9]+'"), r"'md5': '...'"),
  ...    (re.compile(r"Binary\('"), r"Binary(b'"),
  ...    (re.compile(r"'title': u'"), r"'title': '"),
  ...    ]
  >>> reNormalizer = m01.mongo.testing.RENormalizer(patterns)

  >>> def normalize_unicode(data):
  ...     if isinstance(data, dict):
  ...         return {normalize_unicode(k): normalize_unicode(v)
  ...             for k, v in data.items()}
  ...     elif isinstance(data, list):
  ...         return [normalize_unicode(i) for i in data]
  ...     elif isinstance(data, unicode):
  ...         return str(data)
  ...     return data

Convert chunk to simple output used for python 2/3:

  >>> def print_bytes(chunk):
  ...     if isinstance(chunk, bytes):
  ...         chunk = chunk.decode('utf-8')
  ...     print(chunk)

Test the file storage:

  >>> db = m01.fs.testing.getTestDatabase()

  >>> files = m01.fs.testing.getTestCollection()
  >>> files.name == 'test.files'
  True


  >>> storage = m01.fs.testing.SampleFileStorage()
  >>> storage
  <m01.fs.testing.SampleFileStorage object at ...>

Our test setup offers a log handler where we can use like:

  >>> logger.clear()
  >>> print(logger)


FileStorageItem
---------------

The FileStorageItem is implemented as a IMongoStorageItem and provides IFile.
This item can get stored in a IMongoStorage. This is known as the
container/item pattern. This container only defines an add method which
implicit uses the items __name__ as key.

  >>> txt = u'Hello World äöü'
  >>> upload = m01.fs.testing.getFileUpload(txt)
  >>> upload.filename == u'test.txt'
  True

  >>> upload.headers
  {}

  >>> ignored = upload.seek(0)

  >>> print(upload.read().decode('utf-8'))
  Hello World äöü

  >>> ignored = upload.seek(0)

  >>> data = {'title': u'title', 'description': u'description'}
  >>> item = m01.fs.testing.SampleFileStorageItem(data)
  >>> firstID = item._id

Apply the file upload item:

  >>> item.applyFileUpload(upload)

And we've got a log entry:

  >>> print(logger)
  m01.fs DEBUG
    ... FileChunkWriter success

  >>> logger.clear()

Try again:

  >>> item.applyFileUpload(upload)
  >>> print(logger)
  m01.fs DEBUG
    ... FileChunkWriter success

  >>> logger.clear()

Now let's see how our FileItem get enhanced with the chunk info:

  >>> reNormalizer.pprint(item.__dict__)
  {'_id': ObjectId('...'),
   '_m_changed': True,
   '_m_initialized': True,
   '_m_parent': None,
   '_pid': None,
   '_type': 'SampleFileStorageItem',
   '_version': 0,
   'contentType': 'text/plain',
   'created': datetime(..., tzinfo= ...),
   'data': Binary(b'Hello World \xc3\xa4\xc3\xb6\xc3\xbc', 0),
   'description': 'description',
   'filename': 'test.txt',
   'md5': '6d92a019ac8841573340aeaa06713032',
   'size': 18,
   'title': 'title',
   'uploadDate': datetime(..., tzinfo= ...)}

  >>> normalize_unicode(reNormalizer.pprint(item.dump()))
  {'__name__': '...',
   '_id': ObjectId('...'),
   '_pid': None,
   '_type': 'SampleFileStorageItem',
   '_version': 0,
   'contentType': 'text/plain',
   'created': datetime(..., tzinfo= ...),
   'data': Binary(b'Hello World \xc3\xa4\xc3\xb6\xc3\xbc', 0),
   'description': 'description',
   'encoding': None,
   'filename': 'test.txt',
   'md5': '6d92a019ac8841573340aeaa06713032',
   'modified': None,
   'removed': False,
   'size': 18,
   'title': 'title',
   'uploadDate': datetime(..., tzinfo= ...)}

Now let's store our item in our storage:

  >>> key = storage.add(item)
  >>> len(key)
  24

  >>> reNormalizer.pprint(item.__dict__)
  {'_id': ObjectId('...'),
   '_m_changed': True,
   '_m_initialized': True,
   '_m_parent': <m01.fs.testing.SampleFileStorage object at ...>,
   '_pid': None,
   '_type': 'SampleFileStorageItem',
   '_version': 0,
   'contentType': 'text/plain',
   'created': datetime(..., tzinfo= ...),
   'data': Binary(b'Hello World \xc3\xa4\xc3\xb6\xc3\xbc', 0),
   'description': 'description',
   'filename': 'test.txt',
   'md5': '6d92a019ac8841573340aeaa06713032',
   'size': 18,
   'title': 'title',
   'uploadDate': datetime(..., tzinfo= ...)}

  >>> normalize_unicode(reNormalizer.pprint(item.dump()))
  {'__name__': '...',
   '_id': ObjectId('...'),
   '_pid': None,
   '_type': 'SampleFileStorageItem',
   '_version': 0,
   'contentType': 'text/plain',
   'created': datetime(..., tzinfo= ...),
   'data': Binary(b'Hello World \xc3\xa4\xc3\xb6\xc3\xbc', 0),
   'description': 'description',
   'encoding': None,
   'filename': 'test.txt',
   'md5': '6d92a019ac8841573340aeaa06713032',
   'modified': None,
   'removed': False,
   'size': 18,
   'title': 'title',
   'uploadDate': datetime(..., tzinfo= ...)}

Now let's commit the items to mongo:

  >>> transaction.commit()


read
----

Now let's test how we can read files:

  >>> item = storage.get(key)
  >>> reader = item.getFileReader()

and read the file data:

  >>> print(reader.read().decode('utf-8'))
  Hello World äöü

  >>> reader.seek(0)

  >>> ignored = upload.seek(0)

  >>> for chunk in reader:
  ...     print_bytes(chunk)
  Hello World äöü


update
------

We can also update a file by apply a new fileUpload:

  >>> txt = u'Hello NEW World äöü'
  >>> newUpload = m01.fs.testing.getFileUpload(txt)
  >>> newUpload.filename = u'new.txt'
  >>> newUpload.filename == u'new.txt'
  True

  >>> item = storage.get(key)
  >>> item.applyFileUpload(newUpload)

As you can see our logger reports that the previous chunk get marked as tmp and
after upload removed:

  >>> print(logger)
  m01.fs DEBUG
    ... FileChunkWriter success

  >>> logger.clear()

before we commit, let's check if we get a _m_changed marker:

  >>> reNormalizer.pprint(item.__dict__)
  {'_id': ObjectId('...'),
   '_m_changed': True,
   '_m_initialized': True,
   '_m_parent': <m01.fs.testing.SampleFileStorage object at ...>,
   '_pid': None,
   '_type': 'SampleFileStorageItem',
   '_version': 1,
   'contentType': 'text/plain',
   'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'data': Binary(b'Hello NEW World \xc3\xa4\xc3\xb6\xc3\xbc', 0),
   'description': 'description',
   'filename': 'new.txt',
   'md5': '1d411e2de86c5207d2bcc9efe214957f',
   'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'size': 22,
   'title': 'title',
   'uploadDate': datetime(..., tzinfo= ...)}

commit transaction and check the item:

  >>> transaction.commit()

Now let's check the if the storage cache ist empty and we don't get the
cached item without the changed data:

  >>> storage._cache
  {}

Check what we have in mongodb. Note python 2 returns Bytes() and python 3
retuns b''. But both is the same.

  >>> files = m01.fs.testing.getTestCollection()
  >>> for data in files.find():
  ...     reNormalizer.pprint(data)
  {'__name__': '...',
   '_id': ObjectId('...'),
   '_pid': None,
   '_type': 'SampleFileStorageItem',
   '_version': 2,
   'contentType': 'text/plain',
   'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'data': ...,
   'description': 'description',
   'encoding': None,
   'filename': 'new.txt',
   'md5': '1d411e2de86c5207d2bcc9efe214957f',
   'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'removed': False,
   'size': 22,
   'title': 'title',
   'uploadDate': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>)}

Ensure python 2 and 3 data provide the same type:

  >>> from bson.binary import Binary
  >>> if sys.version_info[0] == 2:
  ...     data['data'] == Binary('Hello NEW World \xc3\xa4\xc3\xb6\xc3\xbc', 0)
  ... else:
  ...     data['data'] == b'Hello NEW World \xc3\xa4\xc3\xb6\xc3\xbc'
  True

And let's load the item with our storage:

  >>> item = storage.get(key)
  >>> reNormalizer.pprint(item.__dict__)
  {'_id': ObjectId('...'),
   '_m_changed': False,
   '_m_initialized': True,
   '_m_parent': <m01.fs.testing.SampleFileStorage object at ...>,
   '_pid': None,
   '_type': 'SampleFileStorageItem',
   '_version': 2,
   'contentType': 'text/plain',
   'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'data': Binary(b'Hello NEW World \xc3\xa4\xc3\xb6\xc3\xbc', 0),
   'description': 'description',
   'filename': 'new.txt',
   'md5': '1d411e2de86c5207d2bcc9efe214957f',
   'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'size': 22,
   'title': 'title',
   'uploadDate': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>)}

Now let's read the file data:

  >>> reader = item.getFileReader()
  >>> print_bytes(reader.read())
  Hello NEW World äöü

  >>> reader.seek(0)

  >>> for chunk in reader:
  ...     print_bytes(chunk)
  Hello NEW World äöü


addData
-------

We can also update a file by apply a new fileUpload:

  >>> txt = u'Hello OTHER World äöü'
  >>> filename = u'other.txt'
  >>> contentType = u'text/plain'
  >>> encoding = None

  >>> item = storage.get(key)
  >>> writer = item.getFileWriter()
  >>> writer.addData(txt, filename, contentType, encoding=encoding)

Now let's commit the items to mongo:

  >>> transaction.commit()

As you can see our logger reports that the previous chunk get marked as tmp and
after upload removed:

  >>> print(logger)
  m01.fs DEBUG
    ... FileChunkWriter success

  >>> logger.clear()

Now get the item again and check the data:

  >>> item = storage.get(key)

  >>> item.filename == u'other.txt'
  True

let's check the mongodb data:

  >>> reNormalizer.pprint(item.__dict__)
  {'_id': ObjectId('...'),
   '_m_changed': False,
   '_m_initialized': True,
   '_m_parent': <m01.fs.testing.SampleFileStorage object at ...>,
   '_pid': None,
   '_type': 'SampleFileStorageItem',
   '_version': 3,
   'contentType': 'text/plain',
   'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'data': Binary(b'Hello OTHER World \xc3\xa4\xc3\xb6\xc3\xbc', 0),
   'description': 'description',
   'filename': 'other.txt',
   'md5': '8de2bede646e0fd40aae714c8b369927',
   'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'size': 24,
   'title': 'title',
   'uploadDate': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>)}

check what we will rite back to mongodb:

  >>> normalize_unicode(reNormalizer.pprint(item.dump()))
  {'__name__': '...',
   '_id': ObjectId('...'),
   '_pid': None,
   '_type': 'SampleFileStorageItem',
   '_version': 3,
   'contentType': 'text/plain',
   'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'data': Binary(b'Hello OTHER World \xc3\xa4\xc3\xb6\xc3\xbc', 0),
   'description': 'description',
   'encoding': None,
   'filename': 'other.txt',
   'md5': '8de2bede646e0fd40aae714c8b369927',
   'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'removed': False,
   'size': 24,
   'title': 'title',
   'uploadDate': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>)}

Now let's read the file data:

  >>> reader = item.getFileReader()
  >>> print_bytes(reader.read())
  Hello OTHER World äöü

  >>> reader.seek(0)

  >>> for chunk in reader:
  ...     print_bytes(chunk)
  Hello OTHER World äöü


FileObject
----------

The FileObject provides IFile and IMongoObject.