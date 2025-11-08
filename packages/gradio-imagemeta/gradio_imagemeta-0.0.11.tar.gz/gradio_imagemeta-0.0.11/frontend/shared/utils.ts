 import * as exifr from "exifr";

export const get_coordinates_of_clicked_image = (
	evt: MouseEvent
): [number, number] | null => {
	let image;
	if (evt.currentTarget instanceof Element) {
		image = evt.currentTarget.querySelector("img") as HTMLImageElement;
	} else {
		return [NaN, NaN];
	}

	const imageRect = image.getBoundingClientRect();
	const xScale = image.naturalWidth / imageRect.width;
	const yScale = image.naturalHeight / imageRect.height;
	if (xScale > yScale) {
		const displayed_height = image.naturalHeight / xScale;
		const y_offset = (imageRect.height - displayed_height) / 2;
		var x = Math.round((evt.clientX - imageRect.left) * xScale);
		var y = Math.round((evt.clientY - imageRect.top - y_offset) * xScale);
	} else {
		const displayed_width = image.naturalWidth / yScale;
		const x_offset = (imageRect.width - displayed_width) / 2;
		var x = Math.round((evt.clientX - imageRect.left - x_offset) * yScale);
		var y = Math.round((evt.clientY - imageRect.top) * yScale);
	}
	if (x < 0 || x >= image.naturalWidth || y < 0 || y >= image.naturalHeight) {
		return null;
	}
	return [x, y];
};

/**
 * Extracts metadata from an image file (PNG, JPG/JPEG).
 * This function uses different strategies based on the file type to ensure
 * accurate metadata retrieval.
 *
 * - For JPEGs: It prioritizes and parses custom JSON from the EXIF 'UserComment' tag (ID 37510),
 *   then merges it with other standard, readable EXIF tags.
 * - For PNGs: It reads the simple key-value pairs from the file's text chunks directly.
 *
 * @param fileData - An object with a `url` property pointing to the image file.
 * @param only_custom_metadata - This parameter is now primarily effective for JPEGs. For PNGs,
 *                               all readable text chunks are considered custom metadata.
 * @returns A promise that resolves to a metadata object, or null if the input is invalid.
 */
export async function extractMetadata(
    fileData: any, 
    only_custom_metadata: boolean
): Promise<object | null> {

    if (!fileData?.url) {
        return null;
    }

    const lowercasedUrl = fileData.url.toLowerCase();

    if (lowercasedUrl.endsWith(".svg")) {
        return {};
    }

    try {
        // Extract all raw metadata regardless of file type ---
        const rawMetadata = await exifr.parse(fileData.url, true);
        if (!rawMetadata) {
            return {};
        }

        // Apply logic based on file extension ---

        // --- LOGIC FOR PNG FILES ---
        if (lowercasedUrl.endsWith('.png')) {
            const pngMetadata: { [key: string]: string | number | boolean } = {};
            // For PNGs, exifr reads text chunks into simple key-value pairs.
            // We just need to filter for primitive types.
            for (const [key, value] of Object.entries(rawMetadata)) {
                if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
                    pngMetadata[key] = value;
                }
            }
            return pngMetadata;
        }

        // --- LOGIC FOR JPEG FILES ---
        if (lowercasedUrl.endsWith('.jpg') || lowercasedUrl.endsWith('.jpeg')) {
            let customMetadata: { [key: string]: any } = {};
            const otherMetadata: { [key: string]: string | number | boolean } = {};
            const userCommentKey = 37510;

            // First, specifically look for and process the UserComment tag.
            const userCommentValue = rawMetadata[userCommentKey];
            if (userCommentValue instanceof Uint8Array && userCommentValue.length > 8) {
                try {
                    const decoder = new TextDecoder('utf-8', { fatal: true });
                    const jsonBytes = userCommentValue.slice(8);
                    const jsonString = decoder.decode(jsonBytes).replace(/\0/g, '');
                    customMetadata = JSON.parse(jsonString);
                } catch (e) {
                    console.error("Could not parse JSON from UserComment:", e);
                    otherMetadata['UserComment_RawError'] = 'Failed to parse JSON content.';
                }
            }
            
            // If we only want custom metadata, we are done.
            if (only_custom_metadata) {
                return customMetadata;
            }

            // Otherwise, collect all other readable tags.
            for (const [key, value] of Object.entries(rawMetadata)) {
                // Skip the UserComment key since we've already processed it.
                if (Number(key) === userCommentKey) {
                    continue;
                }
                
                if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
                    // Avoid overwriting a key that might have been in the custom JSON.
                    if (!(key in customMetadata)) {
                        otherMetadata[key] = value;
                    }
                }
            }

            // Merge other tags with our custom data (custom data takes priority).
            return { ...otherMetadata, ...customMetadata };
        }

        // Fallback for any other file types (e.g., .webp, .tiff if exifr supports them)
        // Returns an empty object as we have no special logic for them.
        return {};

    } catch (error) {
        console.error("Failed to extract or process metadata:", error);
        return { error: "Failed to extract metadata" };
    }
}

// A more extensive list of technical EXIF tags. Use if you want to filter heavily.
export const extensiveTechnicalMetadata = new Set([   
    "ImageWidth",
    "ImageHeight",
    "BitsPerSample",
    "Compression",
    "PhotometricInterpretation",
    "FillOrder",
    "DocumentName",
    "ImageDescription", 
    "Orientation",
    "SamplesPerPixel",
    "PlanarConfiguration",
    "YCbCrSubSampling",
    "YCbCrPositioning",
    "XResolution",
    "YResolution",
    "ResolutionUnit",
    "StripOffsets",
    "RowsPerStrip",
    "StripByteCounts",
    "JPEGInterchangeFormat",
    "JPEGInterchangeFormatLength",
    "TransferFunction",
    "WhitePoint",
    "PrimaryChromaticities",
    "YCbCrCoefficients",
    "ReferenceBlackWhite",
    "DateTime",
    "ImageDescription", 
    "Software",
    "HostComputer",
    "Predictor",
    "TileWidth",
    "TileLength",
    "TileOffsets",
    "TileByteCounts",
    "SubIFDs",
    "ExtraSamples",
    "SampleFormat",
    "JPEGTables",

    // === ExifIFD ===
    "ExifVersion",
    "FlashpixVersion",
    "ColorSpace",
    "ComponentsConfiguration",
    "CompressedBitsPerPixel",
    "PixelXDimension",
    "PixelYDimension",
    "MakerNote",     
    "RelatedSoundFile",
    "DateTimeOriginal",
    "CreateDate",
    "SubSecTime",
    "SubSecTimeOriginal",
    "SubSecTimeDigitized",
    "FlashEnergy",
    "SpatialFrequencyResponse",
    "FocalPlaneXResolution",
    "FocalPlaneYResolution",
    "FocalPlaneResolutionUnit",
    "SubjectLocation",
    "SensingMethod",
    "FileSource",
    "SceneType",
    "CFAPattern",
    "Gamma",
    
    // === GPS IFD ===
    "GPSVersionID",
    "GPSLatitudeRef",
    "GPSLatitude",
    "GPSLongitudeRef",
    "GPSLongitude",
    "GPSAltitudeRef",
    "GPSAltitude",
    "GPSTimeStamp",
    "GPSSatellites",
    "GPSStatus",
    "GPSMeasureMode",
    "GPSDOP",
    "GPSSpeedRef",
    "GPSSpeed",
    "GPSTrackRef",
    "GPSTrack",
    "GPSImgDirectionRef",
    "GPSImgDirection",
    "GPSMapDatum",
    "GPSDestLatitudeRef",
    "GPSDestLatitude",
    "GPSDestLongitudeRef",
    "GPSDestLongitude",
    "GPSDestBearingRef",
    "GPSDestBearing",
    "GPSDestDistanceRef",
    "GPSDestDistance",
    "GPSProcessingMethod",
    "GPSAreaInformation",
    "GPSDateStamp",
    "GPSDifferential",
    "GPSHPositioningError",

    // === Interoperability IFD ===
    "InteroperabilityIndex",
    "InteroperabilityVersion",

    // === PNG Specific ===
    "BitDepth",
    "ColorType",
    "Filter",
    "Interlace",
	//==- Adobe Photoshop common ==
	"CreatorTool",
	"CreateDate",
	"ModifyDate",
	"MetadataDate",
	"format",
	"ColorMode",
	"InstanceID",
	"DocumentID",
	"OriginalDocumentID",
    
    // --- Other Common Tags ---
    "ThumbnailOffset",
    "ThumbnailLength",
]);