from application.pycatia_scripts.com_objects import get_app_object

def check_open_parts():
    """Check for open part documents and return their names"""
    try:
        application = get_app_object()
        if not application:
            return []

        documents = application.documents
        part_names = []

        # Check if active document is a Drawing - if so, don't list any parts
        try:
            active_doc = application.active_document
            if hasattr(active_doc, 'name') and active_doc.name.lower().endswith('.catdrawing'):
                return []  # Don't list parts when in a Drawing
        except:
            pass

        for i in range(documents.count):
            doc = documents.item(i + 1)
            if doc.name.endswith('.CATPart'):
                # Only include parts if not in a Drawing context
                clean_name = doc.name.replace('.CATPart', '')
                part_names.append(clean_name)

        return part_names
    except:
        return []
