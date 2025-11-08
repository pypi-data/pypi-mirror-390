<script lang="ts">
    import { createEventDispatcher, onMount, tick } from "svelte";
    import type { SelectData } from "@gradio/utils";
    import { uploadToHuggingFace } from "@gradio/utils";
    import {
        BlockLabel,
        Empty,
        IconButton,
        ShareButton,
        IconButtonWrapper,
        FullscreenButton
    } from "@gradio/atoms";
    import { Download, Image as ImageIcon, Info } from "@gradio/icons";
    import { get_coordinates_of_clicked_image, extractMetadata, extensiveTechnicalMetadata } from "./utils";
    import Image from "./Image.svelte";
    import { DownloadLink } from "@gradio/wasm/svelte";    
    import type { I18nFormatter } from "@gradio/utils";
    import type { FileData } from "@gradio/client";

    /**
     * Props for the ImagePreview component.
     */
    export let value: null | any = null; // Image data with URL and optional metadata.
    export let label: string | undefined = undefined; // Label displayed above the component.
    export let show_label: boolean; // Whether to display the label.
    export let show_download_button: boolean = true; // Whether to show the download button.
    export let selectable: boolean = false; // Whether the image is clickable for coordinate selection.
    export let show_share_button: boolean = false; // Whether to show the share button.
    export let i18n: I18nFormatter; // Formatter for internationalization.
    export let show_fullscreen_button: boolean = true; // Whether to show the fullscreen button.
    export let display_icon_button_wrapper_top_corner: boolean = false; // Whether to position buttons in the top corner.
    export let fullscreen: boolean = false; // Whether the image is in fullscreen mode.
    export let only_custom_metadata: boolean = true; // Whether to filter out technical metadata.
    export let popup_metadata_width: number | string = 400; // Width of the metadata popup (pixels or CSS units).
    export let popup_metadata_height: number | string = 300; // Height of the metadata popup (pixels or CSS units).
    export let height: number | string | undefined = undefined; // Component height (pixels or CSS units).
    export let width: number | string | undefined = undefined; // Component width (pixels or CSS units).

    let metadata: Record<string, any> | null = null; // Extracted image metadata.
    let showMetadataPopup: boolean = false; // Whether the metadata popup is visible.
    let image_container: HTMLElement; // Reference to the image container element.

    // Event dispatcher for component events.
    const dispatch = createEventDispatcher<{
        change: string; // Triggered when the image changes.
        select: SelectData; // Triggered when clicking the image with coordinates.
        fullscreen: boolean; // Triggered when toggling fullscreen mode.
        load_metadata: Record<string, any>; // Triggered when loading metadata.
    }>();

   
    function sleep(ms: number) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    // Reactive: Filters metadata based on only_custom_metadata.
    $: filteredMetadata = only_custom_metadata
        ? Object.fromEntries(
            Object.entries(metadata || {}).filter(([key]) => !extensiveTechnicalMetadata.has(key))
        )
        : metadata;

    // Reactive: Calculates maximum popup width based on component width.
    $: maxPopupWidth = typeof width === 'number' ? width - 20 : typeof width === 'string' ? `calc(${width} - 20px)` : '380px';

   // Reactive: Extracts metadata when value changes (e.g., from gr.Examples).
    $: (async (new_value) => {
        if (new_value) {
            if (new_value.metadata && Object.keys(new_value.metadata).length > 0) {
                metadata = new_value.metadata;
            } else if (new_value.url) {
                try {                    
                    await tick(); 
                    await sleep(100); 
                    metadata = await extractMetadata(new_value, only_custom_metadata);

                } catch (e) {
                    console.error("Error during metadata extraction wrapper:", e);
                    metadata = { error: "Extraction failed." };
                }
            } else {
                metadata = null;
            }
        } else {
            metadata = null;
        }
    })(value);
    
    /**
     * Handles image click to dispatch select event with coordinates.
     * @param evt - Mouse event from clicking the image.
     */
    function handle_click(evt: MouseEvent): void {
        let coordinates = get_coordinates_of_clicked_image(evt);
        if (coordinates) {
            dispatch("select", { index: coordinates, value: null });
        }
    }

    /**
     * Toggles the visibility of the metadata popup.
     */
    function toggleMetadataPopup(): void {
        if (filteredMetadata !== null) {
            showMetadataPopup = !showMetadataPopup;
        }
    }

    /**
     * Dispatches the load_metadata event and closes the popup.
     */
    function dispatchLoadMetadata(): void {
        if (filteredMetadata !== null) {
            dispatch("load_metadata", filteredMetadata);
            closePopup();
        }
    }

    /**
     * Closes the metadata popup.
     */
    function closePopup(): void {
        showMetadataPopup = false;
    }
</script>

<BlockLabel
    {show_label}
    Icon={ImageIcon}
    label={!show_label ? "" : label || i18n("image.image")}
/>
{#if value === null || !value.url}
    <Empty unpadded_box={true} size="large"><ImageIcon /></Empty>
{:else}
    <div class="image-container" bind:this={image_container} style:height style:width>
        <IconButtonWrapper
            display_top_corner={display_icon_button_wrapper_top_corner}
        >
            {#if show_fullscreen_button}
                <FullscreenButton {fullscreen} on:fullscreen />
            {/if}
            {#if metadata !== null}
                <IconButton
                    Icon={Info}
                    label="View Metadata"
                    on:click={(event) => {
                        toggleMetadataPopup();
                        event.stopPropagation();
                    }}
                />
            {/if}
            {#if show_download_button}
                <DownloadLink href={value.url} download={value.orig_name || "image"}>
                    <IconButton Icon={Download} label={i18n("common.download")} />
                </DownloadLink>
            {/if}
            {#if show_share_button}
                <ShareButton
                    {i18n}
                    on:share
                    on:error
                    formatter={async (value) => {
                        if (!value) return "";
                        let url = await uploadToHuggingFace(value, "url");
                        return `<img src="${url}" />`;
                    }}
                    {value}
                />
            {/if}
        </IconButtonWrapper>
        <button on:click={handle_click}>
            <div class:selectable class="image-frame">
                <Image src={value.url} alt="" loading="lazy" on:load />
            </div>
        </button>
    </div>
{/if}

{#if showMetadataPopup && filteredMetadata !== null}
    <div
        class="metadata-popup"
        style:width={typeof popup_metadata_width === 'number' ? `${Math.min(popup_metadata_width, parseFloat(String(maxPopupWidth)))}px` : `min(${popup_metadata_width}, ${maxPopupWidth})`}
        style:height={typeof popup_metadata_height === 'number' ? `${popup_metadata_height}px` : popup_metadata_height}
    >
        <div class="popup-content">
            <button class="close-button" on:click={closePopup}>X</button>
            <h3 class="popup-title">Image Metadata</h3>
            {#if filteredMetadata.error}
                <p>{filteredMetadata.error}</p>
            {:else}
                {#if Object.keys(filteredMetadata).length > 0}
                    <div class="metadata-table-container">
                        <table class="metadata-table">
                            <tbody>
                                {#each Object.entries(filteredMetadata) as [key, val]}
                                    {#if val}
                                        <tr>
                                            <td class="metadata-label">{key}</td>
                                            <td class="metadata-value">{val}</td>
                                        </tr>
                                    {/if}
                                {/each}
                            </tbody>
                        </table>
                    </div>
                    <button class="load-metadata-button" on:click={dispatchLoadMetadata}>Load Metadata</button>
                {:else}
                  <p class="no-metadata-message">No custom metadata found.</p>
                {/if}
            {/if}
        </div>
    </div>
{/if}

<style>
    .image-container {
        height: 100%;
        position: relative;
        min-width: var(--size-20);
    }

    .image-container button {
        width: var(--size-full);
        height: var(--size-full);
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .image-frame :global(img) {
        width: var(--size-full);
        height: var(--size-full);
        object-fit: scale-down;
    }

    .selectable {
        cursor: crosshair;
    }

    :global(.fullscreen-controls svg) {
        position: relative;
        top: 0px;
    }

    :global(.image-container:fullscreen) {
        background-color: black;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    :global(.image-container:fullscreen img) {
        max-width: 90vw;
        max-height: 90vh;
        object-fit: scale-down;
    }

    .image-frame {
        width: auto;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .metadata-popup {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--background-fill-primary, white);
        border: 1px solid var(--border-color-primary);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        border-radius: 8px;
        overflow: hidden;
    }

    .popup-content {
        position: relative;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .popup-title {
        font-weight: bold;
        margin: 0 0 1rem 0;
    }

    .close-button {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: none;
        border: none;
        font-size: 1rem;
        cursor: pointer;
    }

    .metadata-table-container {
        flex: 1;
        overflow: auto;
    }

    .metadata-table {
        width: 100%;
        border-collapse: collapse;
    }

    .metadata-label {
        background: var(--background-fill-secondary, #f5f5f5);
        padding: 0.5rem;
        font-weight: bold;
        text-align: left;
        vertical-align: top;
        width: auto;
    }

    .metadata-value {
        padding: 0.5rem;
        white-space: pre-wrap;
        width: 55%;
        vertical-align: top;
    }

    .load-metadata-button {
        margin-top: 1rem;
        padding: 0.5rem 1rem;
        background-color: var(--button-primary-border-color);
        color: var(--button-primary-text-color);
        border: none;
        border-radius: 4px;
        cursor: pointer;
        align-self: center;
    }

    .load-metadata-button:hover {
        background-color: var(--button-primary-border-color);
    }
</style>