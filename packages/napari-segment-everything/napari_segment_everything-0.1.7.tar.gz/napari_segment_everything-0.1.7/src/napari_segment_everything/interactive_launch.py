import napari

viewer = napari.Viewer()
napari.run()

from napari_segment_everything import segment_everything

viewer.window.add_dock_widget(
    segment_everything.NapariSegmentEverything(viewer)
)
