<script lang="ts">
    import DeleteButton from './DeleteButton.svelte';
</script>

<div class="flex flex-row justify-end gap-2">
    <DeleteButton
        text="Xóa TấT CẢ Bản Ghi"
        prompt={`Bạn có chắc chắn muốn xóa TẤT CẢ bản ghi?`}
        url={`/api/delete-all-recordings`}
        name="tất cả bản ghi"
    />
</div>
