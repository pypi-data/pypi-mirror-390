# GroupDocs.Merger Cloud Python SDK

[GroupDocs.Merger Cloud API](https://products.groupdocs.cloud/merger/python/) empowers developers to integrate advanced document merging and page manipulation functionalities into their Python applications. Supporting over 40 file formats, this REST API allows seamless merging, splitting, and reorganization of document pages, including PDFs, Word documents, Excel spreadsheets, and more. Security features include password protection for documents, while additional file and folder operations streamline cloud storage management. Whether working with cross-format documents or performing complex page manipulations, GroupDocs.Merger Cloud delivers robust tools for secure and efficient document handling across web, desktop, and mobile platforms.

## Requirements

Python 2.7 or 3.4+

## Installation
Install `groupdocs-merger-cloud` with [PIP](https://pypi.org/project/pip/) from [PyPI](https://pypi.org/) by:

```sh
pip install groupdocs-merger-cloud
```

Or clone repository and install it via [Setuptools](http://pypi.python.org/pypi/setuptools): 

```sh
python setup.py install
```

## Getting Started

This example demonstrates merging different Word files seamlessly with a few lines of code:

```python
# For complete examples and data files, please go to https://github.com/groupdocs-merger-cloud/groupdocs-merger-cloud-python-samples
app_sid = "XXXX-XXXX-XXXX-XXXX" # Get AppKey and AppSID from https://dashboard.groupdocs.cloud
app_key = "XXXXXXXXXXXXXXXX" # Get AppKey and AppSID from https://dashboard.groupdocs.cloud
  
documentApi = groupdocs_merger_cloud.DocumentApi.from_keys(app_sid, app_key)
 
item1 = groupdocs_merger_cloud.JoinItem()
item1.file_info = groupdocs_merger_cloud.FileInfo("WordProcessing/sample-10-pages.docx")
item1.pages = [3, 6, 8]
 
item2 = groupdocs_merger_cloud.JoinItem()
item2.file_info = groupdocs_merger_cloud.FileInfo("WordProcessing/four-pages.docx")
item2.start_page_number = 1
item2.end_page_number = 4
item2.range_mode = "OddPages"
 
options = groupdocs_merger_cloud.JoinOptions()
options.join_items = [item1, item2]
options.output_path = "Output/joined-pages.docx"
 
result = documentApi.join(groupdocs_merger_cloud.JoinRequest(options))
```

## Licensing
GroupDocs.Merger Cloud Python SDK licensed under [MIT License](http://github.com/groupdocs-merger-cloud/groupdocs-merger-cloud-python/LICENSE).

## Resources
+ [**Website**](https://www.groupdocs.cloud)
+ [**Product Home**](https://products.groupdocs.cloud/merger)
+ [**Documentation**](https://docs.groupdocs.cloud/display/mergercloud/Home)
+ [**Free Support Forum**](https://forum.groupdocs.cloud/c/merger)
+ [**Blog**](https://blog.groupdocs.cloud/category/merger)

## Contact Us
Your feedback is very important to us. Please feel free to contact us using our [Support Forums](https://forum.groupdocs.cloud/c/merger).