from application.pycatia_scripts.com_objects import get_app_object

def check_open_products():
    """Check for open product documents and return their names"""
    try:
        application = get_app_object()
        if not application:
            return []

        documents = application.documents
        product_names = []

        for i in range(documents.count):
            doc = documents.item(i + 1)
            if doc.name.endswith('.CATProduct'):
                # Remove .CATProduct extension for display
                clean_name = doc.name.replace('.CATProduct', '')
                product_names.append(clean_name)

        return product_names
    except:
        return []
