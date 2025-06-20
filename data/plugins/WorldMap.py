from nicegui import ui

class WorldMap:
    def __init__(self):
        @ui.page('/WorldMap')
        def index():
            with ui.header().classes('bg-primary text-white h-16'):
                with ui.row().classes('w-full h-full items-center justify-between px-4'):
                    ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')
            
            with ui.column().classes('w-full max-w-3xl mx-auto gap-4 p-4'):
                ui.markdown("## World Map")
                
                # Add Leaflet CSS and JS to the body
                ui.add_body_html('''
                    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                ''')
                
                # Create a container for the map with a specific ID
                map_container = ui.html('<div id="world-map" style="width: 100%; height: 500px;"></div>').classes('w-full')
                
                # Initialize the map using add_body_html with DOMContentLoaded event
                ui.add_body_html('''
                    <script>
                        document.addEventListener('DOMContentLoaded', function() {
                            // Initialize the map centered on Australia
                            var map = L.map('world-map').setView([-25.2744, 133.7751], 4);
                            
                            // Add the tile layer
                            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            }).addTo(map);
                            
                            // Force a resize event to ensure the map renders properly
                            setTimeout(function() {
                                map.invalidateSize();
                            }, 100);
                        });
                    </script>
                ''')
                
                