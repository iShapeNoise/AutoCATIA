from operator import itemgetter

from pycatia.in_interfaces.documents import Documents
from pycatia.product_structure_interfaces.product_document import ProductDocument

from application.forms.forms import FormDocumentSave
from application.pycatia_scripts.com_objects import get_app_object


def get_output() -> dict:
    output: dict = {
        'errors': [],
        'data': {},  # can be overwritten with a string for simple success reports otherwise use a mapping.
        'output_file': None
    }

    return output


def check_part_number_exists(documents: Documents, output: dict, part_number: str):
    """
    For creation of new parts and products ensure that the part_number
    doesn't already exist in the session.

    :param documents:
    :param output_:
    :param part_number:
    """

    for doc in documents:
        filename = doc.name
        extension = filename.rsplit(".")[-1].lower()
        if extension == 'catpart' or extension == 'catproduct':
            ref_product = ProductDocument(doc.com_object).product
            if ref_product.part_number == part_number:
                output['errors'].append(f'Part number must be unique in the session. "{part_number}" already in use.')
                return output

    return output


def get_documents(sort_key: str = None, reverse: bool = False) -> tuple[list, dict]:
    application = get_app_object()
    documents = application.documents

    d_list = []

    total_docs = 0
    total_not_saved = 0


    for document in documents:
        d = {
            'filename': document.name,
            'saved': document.is_saved,
            'path': document.path().parent
        }
        d_list.append(d)

        total_docs += 1
        if not document.is_saved:
            total_not_saved += 1

    counter = {
        'total_docs': total_docs,
        'not_saved': total_not_saved,
    }

    if sort_key:
        d_list = sorted(d_list, key=itemgetter(sort_key), reverse=reverse)

    return d_list, counter


def save_documents(form: FormDocumentSave, save_all: bool = False):
    """Save documents - either selected or all"""
    form_documents = form.documents
    application = get_app_object()
    documents = application.documents

    for form_document in form_documents:
        # Save if checkbox is checked OR if save_all is True
        if form_document.save.data or save_all:
            try:
                document = documents.item(form_document.filename.data)
                if not document.is_saved:
                    document.save()
            except:
                # Handle case where document might not exist anymore
                continue


def save_all_documents(documents_list):
    """Save all documents in the list"""
    application = get_app_object()
    if not application:
        return

    catia_documents = application.documents

    for doc_info in documents_list:
        try:
            document = catia_documents.item(doc_info['filename'])
            if not document.is_saved:
                document.save()
        except:
            # Handle case where document might have been closed
            continue
