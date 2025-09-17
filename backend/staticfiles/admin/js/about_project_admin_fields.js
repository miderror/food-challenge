document.addEventListener('DOMContentLoaded', function() {
    const mediaTypeSelect = document.querySelector('#id_media_type');
    const mediaFileRow = document.querySelector('.form-row.field-media_file'); 
    const mediaItemsInlineGroup = document.querySelector('#media_items-group');

    if (!mediaTypeSelect || !mediaFileRow || !mediaItemsInlineGroup) {
        console.error('Не удалось найти один из элементов для управления полями медиа. Проверьте селекторы.');
        console.log("Media Type Select:", mediaTypeSelect);
        console.log("Media File Row:", mediaFileRow);
        console.log("Media Items Group:", mediaItemsInlineGroup);
        return;
    }

    function toggleMediaFields() {
        const selectedType = mediaTypeSelect.value;

        if (selectedType === 'MEDIA_GROUP') {
            mediaFileRow.style.display = 'none';
            mediaItemsInlineGroup.style.display = 'block'; 
        } else if (selectedType) {
            mediaFileRow.style.display = 'block';
            mediaItemsInlineGroup.style.display = 'none';
        } else {
            mediaFileRow.style.display = 'none';
            mediaItemsInlineGroup.style.display = 'none';
        }
    }

    toggleMediaFields();

    mediaTypeSelect.addEventListener('change', toggleMediaFields);
});