import React from 'react'
import { motion } from 'framer-motion'
import { Building2, Users, Cpu, Mail, TrendingUp, AlertCircle, CheckCircle, BrainCircuit, Link } from 'lucide-react'
import { format } from 'date-fns'

const sectionStyles = {
  teal: {
    wrapper: 'bg-white/90 border border-teal/20',
    header: 'bg-teal/10 border-b border-teal/20',
    icon: 'text-teal-dark',
  },
  sun: {
    wrapper: 'bg-white/90 border border-sun/20',
    header: 'bg-sun/20 border-b border-sun/30',
    icon: 'text-clay',
  },
  ink: {
    wrapper: 'bg-white/90 border border-sand-dark',
    header: 'bg-sand-light border-b border-sand-dark',
    icon: 'text-ink',
  },
  clay: {
    wrapper: 'bg-white/90 border border-clay/20',
    header: 'bg-clay/10 border-b border-clay/20',
    icon: 'text-clay',
  },
}

const Section = ({ title, icon: Icon, tone = 'ink', children }) => {
  const styles = sectionStyles[tone] || sectionStyles.ink
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className={`rounded-2xl shadow-sm overflow-hidden ${styles.wrapper}`}>
      <div className={`px-4 py-3 flex items-center gap-2 ${styles.header}`}>
        <Icon className={`w-5 h-5 ${styles.icon}`} />
        <h3 className="font-semibold text-ink">{title}</h3>
      </div>
      <div className="p-4">{children}</div>
    </motion.div>
  )
}

const ScoreBadge = ({ score, label }) => {
  const getColor = (s) => {
    if (s >= 80) return 'bg-teal/15 text-teal-dark border-teal/30'
    if (s >= 60) return 'bg-sun/30 text-ink border-sun/40'
    return 'bg-clay/15 text-clay border-clay/30'
  }
  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${getColor(score)}`}>
      <span className="font-bold">{score}%</span>
      <span className="text-sm font-medium">{label}</span>
    </div>
  )
}

const AnalysisResult = ({ data }) => {
  if (!data) return null
  const { company_name, company_domain, icp_persona, decision_makers, tech_stack, pain_hypothesis, generated_email, score, created_at, analysis } = data

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="bg-ink text-sand rounded-3xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-1">{company_name}</h1>
            <p className="text-sand/70 flex items-center gap-2">
              <Building2 className="w-4 h-4" />
              {company_domain} • {format(new Date(created_at), 'MMM d, yyyy')}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <ScoreBadge score={Math.round((score?.reply_probability || 0) * 100)} label="Reply Probability" />
            <ScoreBadge score={Math.round(score?.quality_score || 0)} label="Lead Quality" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Section title="AI Pain Hypothesis" icon={BrainCircuit} tone="clay">
            <div className="bg-clay/10 border-l-4 border-clay p-4 rounded-r-lg">
              <p className="text-ink leading-relaxed italic">"{pain_hypothesis}"</p>
            </div>
          </Section>

          <Section title="Generated Cold Email" icon={Mail} tone="teal">
            <div className="space-y-4">
              <div className="bg-sand-light p-3 rounded-lg font-mono text-sm text-ink border border-sand-dark">
                <span className="text-ink/50">Subject:</span> {generated_email?.subject}
              </div>
              <div className="bg-white border border-sand-dark rounded-lg p-4 whitespace-pre-wrap text-ink leading-relaxed">
                {generated_email?.body}
              </div>
              <div className="flex flex-wrap gap-2">
                {generated_email?.personalization_elements?.map((elem, idx) => (
                  <span key={idx} className="px-2 py-1 bg-teal/10 text-teal-dark text-xs rounded-full">{elem}</span>
                ))}
                {generated_email?.cta && (
                  <span className="px-2 py-1 bg-sun/30 text-ink text-xs rounded-full">CTA: {generated_email.cta}</span>
                )}
              </div>
            </div>
          </Section>

          <Section title="Company Intelligence" icon={Building2} tone="ink">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-teal-dark mt-0.5" />
                <div>
                  <p className="font-medium text-ink">Target ICP</p>
                  <p className="text-ink/70">{icp_persona}</p>
                </div>
              </div>
              {analysis?.company_summary && (
                <div className="flex items-start gap-3">
                  <Link className="w-5 h-5 text-ink/50 mt-0.5" />
                  <div>
                    <p className="font-medium text-ink">Site Summary</p>
                    <p className="text-ink/70">{analysis.company_summary}</p>
                  </div>
                </div>
              )}
              {analysis?.key_insights?.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {analysis.key_insights.map((insight, idx) => (
                    <span key={idx} className="px-2 py-1 bg-sand-dark text-ink text-xs rounded-full">{insight}</span>
                  ))}
                </div>
              )}
            </div>
          </Section>
        </div>

        <div className="space-y-6">
          <Section title="Decision Makers" icon={Users} tone="teal">
            <div className="space-y-3">
              {decision_makers?.map((dm, idx) => (
                <div key={idx} className="flex items-start gap-3 p-3 bg-sand-light rounded-xl border border-sand-dark">
                  <div className="w-10 h-10 bg-ink text-sand rounded-full flex items-center justify-center font-bold text-sm">
                    {dm.name?.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-ink truncate">{dm.name}</p>
                    <p className="text-sm text-ink/70 truncate">{dm.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="h-1.5 flex-1 bg-sand-dark rounded-full overflow-hidden">
                        <div className="h-full bg-teal-dark rounded-full" style={{ width: `${(dm.relevance_score || 0) * 100}%` }} />
                      </div>
                      <span className="text-xs text-ink/60">{Math.round((dm.relevance_score || 0) * 100)}% match</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Tech Stack" icon={Cpu} tone="ink">
            <div className="flex flex-wrap gap-2">
              {tech_stack?.map((tech, idx) => (
                <div key={idx} className="px-3 py-1.5 bg-ink text-sand rounded-lg text-sm">
                  <span className="font-medium">{tech.technology}</span>
                  <span className="text-sand/70 text-xs ml-1">({tech.category})</span>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Scoring Factors" icon={TrendingUp} tone="sun">
            <div className="space-y-3">
              {score?.factors && Object.entries(score.factors).map(([key, value]) => (
                <div key={key} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-ink/70 capitalize">{key.replace('_', ' ')}</span>
                    <span className="font-medium text-ink">{value}/10</span>
                  </div>
                  <div className="h-2 bg-sand-dark rounded-full overflow-hidden">
                    <div className="h-full bg-clay rounded-full" style={{ width: `${(value / 10) * 100}%` }} />
                  </div>
                </div>
              ))}
              <div className="mt-4 p-3 bg-sun/20 rounded-lg text-sm text-ink">
                <AlertCircle className="w-4 h-4 inline mr-1" />
                {score?.reasoning}
              </div>
            </div>
          </Section>
        </div>
      </div>
    </motion.div>
  )
}

export default AnalysisResult
