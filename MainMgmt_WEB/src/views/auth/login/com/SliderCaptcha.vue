<template>
  <div class="captcha-wrap">
    <!-- 画布 -->
    <div  class="captcha-canvas" ref="canvasRef">
      <img :src="bg" class="captcha-bg" draggable="false" decoding="async" />
      <img :src="piece" class="captcha-piece" :style="{ top: pieceY + 'px', left: pieceLeft + 'px' }" draggable="false" decoding="async"/>

      <div class="captcha-refresh">
        <el-tooltip content="换一张" placement="top">
          <el-button class="captcha-refresh-btn" circle @click="refresh">
            <el-icon :size="16"><RefreshRight /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <!-- 轨道 + 圆形箭头按钮 -->
    <div class="captcha-track">
      <div class="captcha-track-fill" :style="{ width: (barLeft + 20) + 'px' }"></div>
      <button class="captcha-thumb-btn" :class="{ dragging }" :style="{ left: barLeft + 'px' }" @mousedown="startDrag"
        @touchstart="startDrag" aria-label="按住向右拖动完成拼图">
        <svg class="captcha-thumb-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" />
        </svg>
      </button>
    </div>

    <div class="captcha-tip">{{ dragging ? '拖动对齐缺口' : tipText }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import authHttp from '@/api/authHttp'

const emit = defineEmits(['update'])
const props = defineProps({
  initial: { type: Object, default: null }   // 接收父组件传入的初始验证码数据（如果存在就不再请求后端）

})

const bg = ref('')              // 背景图 base64
const piece = ref('')           // 拼图块 base64
const pieceY = ref(0)           // 拼图块在画布中的固定 Y 坐标
const pieceSize = ref(60)       // 拼图块大小
const captchaKey = ref('')      // 验证码 key（后端生成）
const width = 300               // 画布宽度（固定）

const dragging = ref(false)     // 是否正在拖动
const startX = ref(0)           // 鼠标/手指按下的初始 X 坐标
const barLeft = ref(0)          // 滑块按钮的 X 偏移
const pieceLeft = ref(0)        // 拼图块的 X 偏移（与滑块同步）
const tipText = ref('按住滑块，拖动完成拼图') // 提示文案
const verified = ref(false)     // 是否已验证成功
const trackWidth = 300          // 滑轨宽度
const thumbWidth = 40           // 滑块按钮直径
const ready = ref(false)        // 图片是否解码完成

// 将后端返回的数据应用到组件状态，并预加载图片
const applyPayload = async (payload) => {
  bg.value = payload.bg
  piece.value = payload.piece
  pieceY.value = payload.piece_y
  pieceSize.value = payload.piece_size
  captchaKey.value = payload.captcha_key
  barLeft.value = 0
  pieceLeft.value = 0
  verified.value = false
  ready.value = true
}

// 刷新验证码
const refresh = async () => {
  ready.value = false
  const data = await authHttp.getSliderCaptcha()
  await applyPayload(data)
  emit('update', { key: captchaKey.value, offset_x: null, ok: false })
}

// 拖动事件
const startDrag = (e) => {
  if (!ready.value) return
  dragging.value = true
  startX.value = (e.touches ? e.touches[0].clientX : e.clientX)
  window.addEventListener('mousemove', onMove)
  window.addEventListener('touchmove', onMove, { passive: false })
  window.addEventListener('mouseup', endDrag)
  window.addEventListener('touchend', endDrag)
}

// 拖动过程
const onMove = (e) => {
  if (!dragging.value) return
  const clientX = (e.touches ? e.touches[0].clientX : e.clientX)
  let bar = clientX - startX.value
  const barMax = trackWidth - thumbWidth
  bar = Math.max(0, Math.min(barMax, bar))
  barLeft.value = bar

  const pieceMax = width - pieceSize.value
  pieceLeft.value = (bar / barMax) * pieceMax
}

// 结束拖动事件
const endDrag = async () => {
  if (!dragging.value) return
  dragging.value = false
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('touchmove', onMove)
  window.removeEventListener('mouseup', endDrag)
  window.removeEventListener('touchend', endDrag)

  const offset_x = Math.round(pieceLeft.value)
  const key = captchaKey.value

  try {
    const res = await authHttp.verifySlider(key, offset_x)
    if (res.ok) {
      verified.value = true
      emit('update', { key, offset_x, ok: true })
    } else {
      if (res.code === 'expired') {
        ElMessage.warning('验证码已过期')
        await refresh()
      } else if (res.code === 'mismatch') {
        ElMessage.error(res.message)
        await refresh()
      } else {
        ElMessage.warning(res.message)
      }
    }
  } catch (e) {
    ElMessage.error('网络异常，请重试')
  }
}

onMounted(async () => {
  await applyPayload(props.initial)
})
</script>


<style scoped>
/* 容器宽度与后端 CAPTCHA_WIDTH 对齐 */
.captcha-wrap {
  width: 300px;
  margin: 0 auto;
}

/* 画布 */
.captcha-canvas {
  position: relative;
  width: 300px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #2e344d;
  background: #161624;
}

.captcha-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  user-select: none;
}

.captcha-piece {
  position: absolute;
  top: 0;
  left: 0;
  width: v-bind('pieceSize + "px"');
  height: v-bind('pieceSize + "px"');
  pointer-events: none;
  user-select: none;
  filter: drop-shadow(0 0 4px rgba(0, 0, 0, .6));
}

/* 右上角 换一张 */
.captcha-refresh {
  position: absolute;
  right: 10px;
  top: 10px;
  z-index: 2;
}

/* Element Plus 圆形按钮的深色样式 */
:deep(.captcha-refresh-btn.el-button.is-circle) {
  width: 28px;
  height: 28px;
  padding: 0;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid transparent;
  color: #cfeee6;
  backdrop-filter: blur(2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, .35);
  transition: all .2s ease;
}

/* 轨道与圆形箭头按钮 */
.captcha-track {
  position: relative;
  height: 40px;
  margin-top: 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid #2e344d;
  overflow: hidden;
}

.captcha-track-fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  background: rgba(0, 255, 170, 0.08);
  pointer-events: none;
}

/* 拖拽按钮（圆形，内置右箭头） */
.captcha-thumb-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  left: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: grid;
  /* place-items: center;*/
  cursor: grab;
  user-select: none;
  color: #cde7df;
  /* 箭头颜色跟随 currentColor */
  background: radial-gradient(circle at 30% 30%, #1f2436, #141826);
  border: 1px solid #2b324a;
  box-shadow:
    0 6px 14px rgba(0, 0, 0, 0.45),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
  transition: box-shadow .2s ease, transform .1s ease;
}
/* 为子元素添加居中样式 */
.captcha-thumb-btn > * {
  place-self: center;
}

.captcha-thumb-btn.dragging {
  cursor: grabbing;
  box-shadow:
    0 8px 18px rgba(0, 0, 0, 0.55),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  transform: translateY(-50%) scale(0.98);
}

.captcha-thumb-icon {
  width: 18px;
  height: 18px;
}

/* 提示 */
.captcha-tip {
  width: 100%;
  text-align: center;
  color: #8b93a7;
  font-size: 13px;
  margin-top: 6px;
}

</style>
