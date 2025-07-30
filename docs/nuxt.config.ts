export default defineNuxtConfig({
    devtools: { enabled: true },
    extends: ["docus"],
    components: [
        '~/components',
    ],
    alias: {
        '@theme': '~/theme'
    },
    content: {
        build: {
            markdown: {
                highlight: {
                    theme: {
                        default: 'github-light',
                        dark: 'github-dark'
                    },
                    langs: [
                        'python', 'markdown', 'bash', 'json', 'yaml', 'html', 'css', 'javascript', 'typescript',
                    ]
                }
            }
        }
    }
})
