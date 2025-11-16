/* eslint-env node */
module.exports = {
  root: true,
  extends: ['plugin:vue/vue3-essential', 'eslint:recommended'],
  parserOptions: {
    ecmaVersion: 'latest'
  },
  rules: {
    'vue/multi-word-component-names': 'off', // 多名词提示
    'vue/no-multiple-template-root': 'off', // template 中没有数据
    'vue/valid-template-root': 'off', // 取消有效模板根节点检查
    'no-async-promise-executor': 'off', // 异步函数提示
    'no-useless-escape': 'off', //转义字符
    'no-unused-vars': 'off', // 取消未使用变量的警告
    // 'vue/no-unused-vars': 'off', // 取消 Vue 未使用变量的警告
    'vue/no-unused-vars': ['error', {
      'ignorePattern': '^props$',  // 忽略名为 'props' 的变量
    }],
  }
}