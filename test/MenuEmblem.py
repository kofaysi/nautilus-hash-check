import gi

gi.require_version('Nautilus', '3.0')
from gi.repository import Nautilus, GObject

class EmblemManagerExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        pass

    def apply_emblem(self, menu, files, emblem_name):
        for file in files:
            if file.can_write():
                file.add_emblem(emblem_name)

    def remove_emblems(self, menu, files):
        for file in files:
            if file.can_write():
                file.add_string_attribute("metadata::emblems", "")

    def get_file_items(self, window, files):
        if len(files) == 0:
            return

        parent_item = Nautilus.MenuItem(
            name="EmblemManagerExtension::ParentItem",
            label="Manage Emblems",
            tip="Add or remove emblems",
            icon="dialog-information"
        )

        submenu = Nautilus.Menu()
        parent_item.set_submenu(submenu)

        add_important_item = Nautilus.MenuItem(
            name="EmblemManagerExtension::AddImportant",
            label="Add Important Emblem",
            tip="Apply the emblem-important emblem"
        )
        add_important_item.connect('activate', self.apply_emblem, files, "emblem-important")
        submenu.append_item(add_important_item)

        add_verified_item = Nautilus.MenuItem(
            name="EmblemManagerExtension::AddVerified",
            label="Add Verified Emblem",
            tip="Apply the emblem-hash-verified emblem"
        )
        add_verified_item.connect('activate', self.apply_emblem, files, "emblem-hash-verified")
        submenu.append_item(add_verified_item)

        remove_emblems_item = Nautilus.MenuItem(
            name="EmblemManagerExtension::RemoveEmblems",
            label="Remove All Emblems",
            tip="Remove all emblems from the file"
        )
        remove_emblems_item.connect('activate', self.remove_emblems, files)
        submenu.append_item(remove_emblems_item)

        return [parent_item]
