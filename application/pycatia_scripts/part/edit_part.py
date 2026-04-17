from application.pycatia_scripts.com_objects import get_app_object

def check_open_parts():
    """Check for open part documents and return their names"""
    try:
        application = get_app_object()
        if not application:
            return []

        documents = application.documents
        part_names = []

        for i in range(documents.count):
            doc = documents.item(i + 1)
            if doc.name.endswith('.CATPart'):
                # Remove .CATPart extension for display
                clean_name = doc.name.replace('.CATPart', '')
                part_names.append(clean_name)

        return part_names
    except:
        return []
