<template>
  <div class="resume">
    <!-- 个人信息模块优化 -->
    <el-card class="box-card profile-card">
      <div class="card-content">
        <h1 class="name">张三</h1>
        <p class="position">运维工程师</p>
        <el-divider class="custom-divider" />
        <div class="contact-info">
          <div class="contact-item">
            <el-icon><Clock /></el-icon>
            <span>8年工作经验</span>
          </div>
          <div class="contact-item">
            <el-icon><Medal /></el-icon>
            <span>本科</span>
          </div>
          <div class="contact-item">
            <el-icon><Message /></el-icon>
            <span>844709972@qq.com</span>
          </div>
          <div class="contact-item">
            <el-icon><Iphone /></el-icon>
            <span>17704058457</span>
          </div>
          <div class="contact-item">
            <el-icon><Location /></el-icon>
            <span>深圳 · 可远程</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 个人优势模块 -->
<el-card class="box-card">
  <h3 class="section-title">
    <el-icon><Star /></el-icon>
    个人优势
  </h3>
  <ul class="advantages-list">
    <li>熟练掌握运维自动化工具，能够大幅提升工作效率</li>
    <li>具有较强的故障诊断和问题解决能力</li>
    <li>丰富的云平台运维经验，熟悉主流云服务平台</li>
    <li>精通容器化技术，能够独立设计、部署高可用的云原生架构</li>
    <li>强烈的责任心和团队协作精神，能快速适应变化的工作环境</li>
  </ul>
</el-card>

    <!-- 技能模块优化 -->
    <el-card class="box-card">
  <h3 class="section-title">
    <el-icon><Tools /></el-icon>
    技术栈熟练度
  </h3>
  <el-row :gutter="20" class="skills-wrapper">
    <el-col v-for="(skill, index) in skillsWithProgress" :key="index" :span="4">
      <div class="skill-item">
        <!-- 技能名称 -->
        <span class="skill-name">{{ skill.name }}</span>
        <!-- 技能进度条 -->
        <div class="progress-container">
          <div class="progress-bar">
            <AnimatedProgress :percentage="skill.proficiency" :stroke-width="12" :show-text="false" color="#000" />
          </div>
          <!-- 显示百分比 -->
          <span class="skill-percentage">{{ skill.proficiency }}%</span>
        </div>
      </div>
    </el-col>
  </el-row>
</el-card>

    <!-- 工作经历优化 -->
    <el-card class="box-card">
      <h3 class="section-title">
        <el-icon><Clock /></el-icon>
        工作经历
      </h3>
      <el-timeline>
        <el-timeline-item v-for="(experience, index) in workExperiences" :key="index" :timestamp="experience.timestamp" :hollow="true" :color="index === 0 ? '#409eff' : '#e4e7ed'" placement="top">
          <div class="timeline-content">
            <h4 class="position-title">
              {{ experience.position }}
              <el-tag size="small" effect="plain">{{ experience.company }}</el-tag>
            </h4>
            <ul class="experience-list">
              <li v-for="(item, i) in experience.responsibilities" :key="i">{{ item }}</li>
            </ul>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 项目经验优化 -->
    <el-card class="box-card">
      <h3 class="section-title">
        <el-icon><TrophyBase /></el-icon>
        项目经验
      </h3>
      <el-row :gutter="20" class="project-grid">
        <el-col v-for="(project, index) in projects" :key="index" :xs="24" :sm="12" :md="8">
          <el-card :header="project.name" shadow="hover" class="project-card">
            <template #header>
              <div class="project-header">
                <span>{{ project.name }}</span>
                <el-tag type="warning" size="small">{{ project.duration }}</el-tag>
              </div>
            </template>
            <div class="project-content">
              <p class="project-role">
                <el-icon><User /></el-icon>
                {{ project.role }}
              </p>
              <el-collapse>
                <el-collapse-item title="项目详情">
                  <ul class="project-details">
                    <li v-for="(detail, i) in project.details" :key="i">{{ detail }}</li>
                  </ul>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 教育背景优化 -->
    <el-card class="box-card">
      <h3 class="section-title">
        <el-icon><Reading /></el-icon>
        教育背景
      </h3>
      <div class="education-item">
        <div class="edu-left">
          <el-image src="https://via.placeholder.com/80" class="university-logo" />
        </div>
        <div class="edu-right">
          <h4>某大学 · 软件工程</h4>
          <p class="edu-meta">
            <span>2012.09 - 2016.06</span>
            <el-divider direction="vertical" />
            <span>本科</span>
            <el-divider direction="vertical" />
            <span>GPA 3.8/4.0</span>
          </p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Message, Iphone, Location, Star, Clock, TrophyBase, User, Reading } from '@element-plus/icons-vue';
import AnimatedProgress from '@/components/AnimatedProgress.vue';

const skillsWithProgress = [
  { name: 'Linux', proficiency: 90 },
  { name: 'Python', proficiency: 85 },
  { name: 'Docker', proficiency: 80 },
  { name: 'Kubernetes', proficiency: 75 },
  { name: 'CI/CD', proficiency: 88 },
  { name: 'Nginx', proficiency: 80 },
  { name: 'Prometheus', proficiency: 70 },
  { name: 'Grafana', proficiency: 65 },
  { name: 'Ansible', proficiency: 75 },
  { name: 'Terraform', proficiency: 60 },
  { name: 'AWS', proficiency: 80 },
  { name: 'Jenkins', proficiency: 70 },
  { name: 'ELK Stack', proficiency: 75 },
  { name: 'Zabbix', proficiency: 65 },
  { name: 'MySQL', proficiency: 90 },
  { name: 'Redis', proficiency: 80 }
];


const workExperiences = ref([
  {
    timestamp: '2023 - 至今',
    position: '高级运维工程师',
    company: '某互联网公司',
    responsibilities: [
      '主导云原生架构迁移，容器化部署率从40%提升至85%',
      '设计并实施CI/CD流水线，部署效率提升60%',
      '构建基于Prometheus的全链路监控体系，MTTR降低30%',
      '主导运维自动化平台开发，运维效率提升40%'
    ]
  },
  {
    timestamp: '2019 - 2023',
    position: '运维工程师',
    company: '某科技公司',
    responsibilities: ['管理200+台服务器集群，保障99.99%可用性', '设计灾备方案，RTO从4小时缩短至30分钟', '实施自动化运维系统，人力成本降低25%', '优化系统架构，服务器资源利用率提升35%']
  }
]);

const projects = ref([
  {
    name: '自动化运维平台',
    role: '项目负责人',
    duration: '2023.03 - 2023.12',
    details: ['采用Python+Django开发核心模块', '集成Ansible实现批量操作', '实现自动化部署、监控告警、日志分析功能', '节省30%运维人力成本']
  },
  {
    name: '云监控系统',
    role: '技术负责人',
    duration: '2022.06 - 2022.12',
    details: ['基于Prometheus+Grafana构建监控体系', '开发自定义Exporter监控业务指标', '实现多维度告警策略', '服务器故障发现时间缩短至5分钟内']
  }
]);
</script>

<style scoped>
.resume {
  margin: 20px auto;
  padding: 0 20px;
}

.box-card {
  margin-bottom: 24px;
  transition: transform 0.3s;
}

.box-card:hover {
  transform: translateY(-4px);
}

.profile-card {
  text-align: center;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 3px solid #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.badge {
  position: absolute;
  right: -10px;
  bottom: 10px;
  background: #409eff;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.name {
  font-size: 28px;
  margin: 16px 0 8px;
}

.position {
  font-size: 18px;
  color: #606266;
  margin-bottom: 12px;
}

.custom-divider {
  margin: 16px 0;
}

.contact-info {
  display: flex;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;

  margin-bottom: 20px;
}

.skills-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.skill-tag {
  font-size: 14px;
  padding: 8px 16px;
  transition: all 0.3s;
}

.skill-tag:hover {
  transform: scale(1.05);
}

.timeline-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.position-title {
  margin: 0 0 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.experience-list {
  margin: 0;
  padding-left: 20px;
  color: #5e6d82;
  line-height: 1.8;
}

.project-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.project-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.project-role {
  color: #409eff;
  margin: 0 0 12px;
}

.project-details {
  margin: 0;
  padding-left: 20px;
  color: #5e6d82;
  line-height: 1.6;
}

.education-item {
  display: flex;
  gap: 24px;
  align-items: center;
}

.university-logo {
  width: 80px;
  height: 80px;
  border-radius: 8px;
}

.edu-right h4 {
  margin: 0 0 8px;
  color: #303133;
}

.edu-meta {
  color: #909399;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 个人优势 */
.advantages-list {
  margin: 0;
  padding-left: 20px;
  line-height: 1.8;
}

.advantages-list li {
  margin-bottom: 10px;
}

/* 技术栈熟练度 */
.skills-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.skill-item {
  text-align: left;
  display: flex;
  align-items: flex-start; /* 左对齐 */
  gap: 8px;
}

.skill-name {
  font-size: 14px;
  text-align: left;
  width: 130px;
}

.progress-container {
  display: flex;
  justify-content: space-between;  /* 左右分布 */
  align-items: center;  /* 垂直居中 */
  width: 100%; /* 占满父容器的宽度 */
}

.progress-bar {
  flex: 1;  /* 使进度条占据大部分空间 */
  margin-right: 8px;  /* 进度条与百分比之间的空隙 */
}

.skill-percentage {
  font-size: 12px;
  white-space: nowrap;  /* 防止百分比换行 */
}

.el-progress {
  width: 100%; /* 进度条宽度调整为100% */
  margin-right: 10px; /* 给进度条右侧留出一些间距 */
}

</style>
