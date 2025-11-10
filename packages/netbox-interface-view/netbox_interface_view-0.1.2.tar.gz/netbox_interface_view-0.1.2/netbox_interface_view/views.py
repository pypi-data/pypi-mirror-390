from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from dcim.models import Device, Interface
from ipam.models import VLAN
from utilities.views import register_model_view


@register_model_view(Device, name='interface-grid')
class InterfaceGridView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ["dcim.change_device", "dcim.view_device"]
    template_name = "netbox_interface_view/interface_grid.html"


    def get(self, request, device_id):
        device = get_object_or_404(Device, pk=device_id)
        
        # Get grid dimensions from custom fields (with defaults)
        grid_rows = device.custom_field_data.get('grid_rows', 2)
        grid_columns = device.custom_field_data.get('grid_columns', 24)
        
        # Get grid order preference (column-major by default)
        grid_order = request.GET.get('grid_order', 'column-major')
        
        # Get filter parameters
        filter_types = request.GET.getlist('exclude_type', [])
        
        # Get all interfaces for this device
        interfaces = Interface.objects.filter(device=device).order_by('name')
        
        # Apply type filters
        if filter_types:
            interfaces = interfaces.exclude(type__in=filter_types)
        
        # Build interface data with VLAN colors and connection status
        interface_list = []
        for idx, interface in enumerate(interfaces):
            # Get VLAN colors
            untagged_vlan = None
            tagged_vlans = []
            
            if interface.untagged_vlan:
                vlan_color = interface.untagged_vlan.custom_field_data.get('color', '#cccccc')
                untagged_vlan = {
                    'id': interface.untagged_vlan.id,
                    'vid': interface.untagged_vlan.vid,
                    'name': interface.untagged_vlan.name,
                    'color': vlan_color
                }
            
            for vlan in interface.tagged_vlans.all():
                vlan_color = vlan.custom_field_data.get('color', '#cccccc')
                tagged_vlans.append({
                    'id': vlan.id,
                    'vid': vlan.vid,
                    'name': vlan.name,
                    'color': vlan_color
                })
            
            # Check connection status
            is_connected = interface.cable is not None
            is_enabled = interface.enabled
            
            interface_list.append({
                'id': interface.id,
                'name': interface.name,
                'type': interface.type,
                'description': interface.description,
                'enabled': is_enabled,
                'connected': is_connected,
                'untagged_vlan': untagged_vlan,
                'tagged_vlans': tagged_vlans,
                'original_index': idx + 1,  # 1-based index for display
            })
        
        # Get unique interface types for filter dropdown
        # Extract from already-fetched interfaces to avoid extra query
        all_interface_types = list(set(iface['type'] for iface in interface_list))
        all_interface_types.sort()
        
        # Calculate empty cells
        empty_cells_count = max(0, (grid_rows * grid_columns) - len(interface_list))
        empty_cells = range(empty_cells_count)
        
        # For column-major display, keep interfaces in original order
        # The template will render them in CSS grid which fills row by row
        # So we need to transform positions to achieve column-major visual layout
        # For a 2x24 grid with column-major: 1,2 in col1, 3,4 in col2, etc.
        # This means we need to reorder: [1,2,3,4,5,6...] -> [1,3,5...2,4,6...]
        if grid_order == 'column-major':
            # Transform to column-major: split into rows, then interleave
            reordered_interfaces = []
            for col in range(grid_columns):
                for row in range(grid_rows):
                    idx = col * grid_rows + row
                    if idx < len(interface_list):
                        reordered_interfaces.append(interface_list[idx])
            interface_list = reordered_interfaces
        
        context = {
            'device': device,
            'interfaces': interface_list,
            'grid_rows': grid_rows,
            'grid_columns': grid_columns,
            'total_cells': grid_rows * grid_columns,
            'empty_cells': empty_cells,
            'interface_types': all_interface_types,
            'excluded_types': filter_types,
            'grid_order': grid_order,
        }
        
        return render(request, 'netbox_interface_view/interface_grid.html', context)
