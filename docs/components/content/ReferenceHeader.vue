<template>
    <div class="reference-header py-4 border-b border-neutral-200 dark:border-neutral-800">
        <!-- Top section with icon and type badge -->
        <div class="flex items-center gap-3 mb-3">
            <UIcon v-if="navigation?.icon" :name="navigation.icon" class="text-primary-500 flex-shrink-0" />

            <UBadge v-if="type" :color="getBadgeColor(type)" class="uppercase" variant="outline">
                {{ type }}
            </UBadge>
        </div>

        <!-- Description section -->
        <p v-if="description" class="text-neutral-700 dark:text-neutral-300 mb-3">
            {{ description }}
        </p>

        <!-- Type annotation section -->
        <div v-if="typing" class="mb-3">
            <UBadge color="neutral" variant="subtle" class="text-xs">Type</UBadge>
            <ProseCode class="ml-2 text-sm bg-neutral-100 dark:bg-neutral-800 px-2 py-0.5 rounded" :lang="lang">{{
                typing }}</ProseCode>
        </div>

        <slot></slot>
    </div>
</template>

<script setup>
const props = defineProps({
    description: {
        type: String,
        default: ''
    },
    type: {
        type: String,
        default: ''
    },
    lang: {
        type: String,
        default: ''
    },
    typing: {
        type: String,
        default: ''
    },
    navigation: {
        type: Object,
        default: () => ({})
    }
})

/**
 * Returns the appropriate badge color based on the API object type
 */
function getBadgeColor(type) {
    const colorMap = {
        'variable': 'info',
        'method': 'success',
        'class': 'primary',
        'function': 'warning',
        'module': 'error',
        'property': 'secondary'
    }

    return colorMap[type.toLowerCase()] || 'neutral'
}
</script>

<style scoped>
.reference-header {
    position: relative;
}
</style>

<style scoped>
.reference-header {
    position: relative;
}
</style>