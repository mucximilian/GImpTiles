# -*- coding: utf-8 -*-
import psycopg2
import svgwrite
import os

from gimpfu import *
from TileRenderer import TileRenderer

class TileRendererGimp(TileRenderer):
    def __init__(self, bbox, zoom_levels, brush_settings, tile_size, out_dir):
        
        conn_zoom = psycopg2.connect('dbname=gimp_osm_styles'
                	'user=gis '
                	'password=gis'
                	'host=localhost '
                	'port=5432')    
        curs_zoom = conn_zoom.cursor()
        
        ########################################################################
        # Zoom level loop
        for zoom in zoom_levels:
            
            tiling_data = self.get_tiling_data(bbox, zoom)            
            print tiling_data
    
            out_dir_zoom = out_dir + str(zoom) + "/"
            if not os.path.exists(out_dir_zoom):
                os.makedirs(out_dir_zoom)
            
            # Get OSM tags and styles for zoom level
            sql = """
                SELECT * FROM get_line_tags_and_style(%s)
            """                        
            curs_zoom.execute(
                sql, (
                    zoom
                )
            )
            
            ####################################################################            
            # X-direction loop
            for x in range(tiling_data[0][0], tiling_data[1][0] + 1):
                
                indent = "  "
                print (indent + "row " 
                    + str(x + tiling_data[2][0] - tiling_data[1][0]) + "/" 
                    + str(tiling_data[2][0]) + " (" + str(x) + ")")
                
                out_dir_zoom_x = out_dir_zoom + str(x) + "/"
                if not os.path.exists(out_dir_zoom_x):
        			os.makedirs(out_dir_zoom_x)
    
                ################################################################
                # Y-direction loop
                for y in range(tiling_data[0][1], tiling_data[1][1] + 1):
                                    
                    ul_x = self.origin_x + x * tiling_data[3]
                    ul_y = self.origin_y - y * tiling_data[3]
                    lr_x = ul_x + tiling_data[3]
                    lr_y = ul_y - tiling_data[3]
                                    
                    print indent + indent + "tile " + str(x) + "/" + str(y)

                    # Create GIMP image with white background layer
                    image = pdb.gimp_image_new(tile_size, tile_size, RGB)    
                    pdb.gimp_context_set_background((255,255,255,255))                    
                    background = pdb.gimp_layer_new(
                        image,
                        tile_size,
                        tile_size,
                        RGBA_IMAGE,
                        "background",
                        100,
                        NORMAL_MODE
                    )    
                    pdb.gimp_image_insert_layer(image, background, None, 0)    				
                    pdb.gimp_edit_fill(background, BACKGROUND_FILL)
                    
                    # Get svg tiles from database                    
                    conn_osm = psycopg2.connect('dbname=osm_muc '
                        'user=gis '
                        'password=gis'
                        'host=localhost '
                        'port=5432')    
                    curs_osm = conn_osm.cursor()

                    ############################################################
                    # Geometry feature loop START
                    for row in curs_zoom.fetchall():
                        sql_selection = get_selection_tags(row[1])
                        line_style = {
                            row[3],
                            row[4],
                            row[5],
                            row[6],
                            row[7]
                        }
                        
                        sql = """
                            SELECT 
                            	ROW_NUMBER() OVER (ORDER BY osm_id) AS id,
                            	svg
                            FROM (
                            	SELECT
                            		get_scaled_svg(
                            			way,
                            			%s,
                            			%s,
                            			%s,
                            			%s,
                            			%s
                            		) AS svg,
                            		*
                            	FROM planet_osm_line  
                            	WHERE ST_Intersects ( 
                            		way, 
                            		get_tile_bbox(
                            			%s,
                            			%s,
                            			%s,
                            			%s,
                            			%s,
                            			%s
                            		) 
                            	)
                            ) t
                            WHERE (""" + sql_selection + ")"      
                            
                        # Get SVG tile geometry from database
                        curs_osm.execute(sql, (
                            ul_x,
                            ul_y,
                            lr_x,
                            lr_y,
                            tile_size,
                            ul_x,
                            ul_y,
                            lr_x,
                            lr_y,
                            tile_size,
                            line_style[1]
                            )
                        )
                        
                        # Create image layer for geometry feature
                        layer = pdb.gimp_layer_new(
                            image,
                            tile_size,
                            tile_size,
                            RGBA_IMAGE,
                            sql_selection,
                            100,
                            NORMAL_MODE
                        )    
                        pdb.gimp_image_insert_layer(image, layer, None, 0)    				
                        
                        # Style settings
                        pdb.gimp_context_set_brush(line_style[0])
                        pdb.gimp_context_set_brush_size(line_style[1])
                        pdb.gimp_context_set_dynamics(line_style[4])
                        pdb.gimp_context_set_foreground((
                            line_style[2][0],
                            line_style[2][1],
                            line_style[2][2],
                            line_style[3]
                        ))
                        pdb.gimp_context_push()
                    
                        # Create temporary SVG drawing from geometry features
                        dwg = svgwrite.Drawing(
                            height = tile_size,
                            width = tile_size
                        )
                    
                        # Import SVG data into SVG drawing from database
                        for row in curs_osm.fetchall():
                            path = dwg.path(d=row[3])
                            path_str = path.tostring()
                    
                            pdb.gimp_vectors_import_from_string(
                                image, 
                                path_str, 
                                -1, 1, 1,
                            )
                    
                        print "vectors: " + str(len(image.vectors))
                        
                        # Draw vectors into GIMP image layer
                        # TO DO: emulate brush dynamics?????
                        for vector in image.vectors:
                            pdb.gimp_edit_stroke_vectors(layer, vector)
                        
                        curs_osm.close()

                    # Geometry feature loop END
                    ############################################################
                    
                    # Assign the Y value as the file name
                    out_path = out_dir_zoom_x + str(y) + ".png"        
                    print "saving file: " + out_path
                    
                    pdb.file_png_save_defaults(
                        image, 
                        layer,
                        out_path,
                        out_path
                    )
                     
                # Y-direction loop END
                ################################################################
                
                conn_osm.close()
            
            # Y-direction loop END
            ####################################################################
                
            curs_zoom.close()
            
        # Zoom-level loop END
        ########################################################################
        
        conn_zoom.close()       