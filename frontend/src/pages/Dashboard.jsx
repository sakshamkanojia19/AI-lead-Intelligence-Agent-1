import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, History, ChevronRight, Radar, Sparkles, MailCheck, Target } from 'lucide-react'
import LeadForm from '../components/LeadForm'
import AnalysisResult from '../components/AnalysisResult'
import { getLeads } from '../services/api'
import { format } from 'date-fns'

const Dashboard = () => {
  const [activeView, setActiveView] = useState('form')
  const [currentResult, setCurrentResult] = useState(null)
  const [recentLeads, setRecentLeads] = useState([])

  useEffect(() => { fetchRecentLeads() }, [])

  const fetchRecentLeads = async () => {
    try {
      const data = await getLeads({ limit: 5 })
      setRecentLeads(data.leads)
    } catch (error) { console.error('Failed to fetch leads:', error) }
  }

  const handleSuccess = (result) => {
    setCurrentResult(result)
    setActiveView('result')
    fetchRecentLeads()
  }

  const avgQuality = recentLeads.length > 0
    ? Math.round(recentLeads.reduce((acc, l) => acc + (l.score?.quality_score || 0), 0) / recentLeads.length)
    : 0

  return (
    <div className="min-h-screen bg-sand relative overflow-hidden">
      <div className="pointer-events-none absolute -top-20 -right-24 h-80 w-80 rounded-full bg-gradient-to-br from-teal/30 to-transparent blur-2xl" />
      <div className="pointer-events-none absolute top-40 -left-24 h-72 w-72 rounded-full bg-gradient-to-br from-sun/40 to-transparent blur-2xl" />

      <nav className="relative z-10 bg-sand/80 backdrop-blur border-b border-sand-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-ink text-sand rounded-xl flex items-center justify-center font-bold">AI</div>
              <div>
                <span className="font-display text-lg font-bold text-ink">Lead Intelligence</span>
                <p className="text-xs text-ink/60">Single-Agent Outreach</p>
              </div>
            </div>
            <button
              onClick={() => { setActiveView('form'); setCurrentResult(null) }}
              className="flex items-center gap-2 px-4 py-2 bg-ink text-sand rounded-xl text-sm font-semibold shadow-sm hover:shadow-glow transition"
            >
              <Plus className="w-4 h-4" />New Research
            </button>
          </div>
        </div>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white/80 rounded-2xl shadow-sm border border-sand-dark p-4">
              <div className="flex items-center gap-2 mb-4 text-ink/80">
                <History className="w-5 h-5" />
                <h3 className="font-semibold">Recent Leads</h3>
              </div>
              <div className="space-y-3">
                {recentLeads.map((lead) => (
                  <button
                    key={lead.id}
                    onClick={() => { setCurrentResult(lead); setActiveView('result') }}
                    className="w-full text-left p-3 rounded-xl hover:bg-sand-light transition border border-transparent hover:border-sand-dark group"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-ink group-hover:text-teal-dark">{lead.company_name}</p>
                        <p className="text-xs text-ink/50 mt-1">
                          {format(new Date(lead.created_at), 'MMM d, h:mm a')}
                        </p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-ink/40 group-hover:text-teal-dark" />
                    </div>
                    <div className="flex gap-2 mt-2">
                      <span className="text-xs px-2 py-0.5 bg-teal/10 text-teal-dark rounded-full">
                        {Math.round((lead.score?.reply_probability || 0) * 100)}% reply
                      </span>
                      <span className="text-xs px-2 py-0.5 bg-sun/20 text-ink rounded-full">
                        {Math.round(lead.score?.quality_score || 0)} quality
                      </span>
                    </div>
                  </button>
                ))}
                {recentLeads.length === 0 && <p className="text-sm text-ink/50 text-center py-4">No leads yet</p>}
              </div>
            </div>

            <div className="bg-ink text-sand rounded-2xl shadow-lg p-4">
              <h4 className="font-semibold mb-3">Agent Stats</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-sand/70">Total</span><span className="font-bold">{recentLeads.length}</span></div>
                <div className="flex justify-between"><span className="text-sand/70">Avg Quality</span><span className="font-bold">{avgQuality}%</span></div>
                <div className="flex justify-between"><span className="text-sand/70">Avg Reply</span><span className="font-bold">{recentLeads.length > 0 ? Math.round(recentLeads.reduce((acc, l) => acc + (l.score?.reply_probability || 0), 0) / recentLeads.length * 100) : 0}%</span></div>
              </div>
            </div>

            <div className="bg-white/80 rounded-2xl border border-sand-dark p-4">
              <h4 className="font-semibold mb-3">Agent Loop</h4>
              <div className="space-y-3 text-sm text-ink/70">
                <div className="flex items-center gap-2"><Radar className="w-4 h-4 text-teal-dark" />Scrape company signals</div>
                <div className="flex items-center gap-2"><Target className="w-4 h-4 text-teal-dark" />Find decision makers</div>
                <div className="flex items-center gap-2"><Sparkles className="w-4 h-4 text-teal-dark" />Generate pain hypothesis</div>
                <div className="flex items-center gap-2"><MailCheck className="w-4 h-4 text-teal-dark" />Personalize outreach</div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-3">
            <AnimatePresence mode="wait">
              {activeView === 'form' ? (
                <motion.div key="form" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
                  <LeadForm onSuccess={handleSuccess} />
                </motion.div>
              ) : (
                <motion.div key="result" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
                  <div className="mb-4 flex items-center justify-between">
                    <button onClick={() => setActiveView('form')} className="text-sm text-ink/60 hover:text-teal-dark">Back to form</button>
                    <span className="text-sm text-ink/50">Research complete</span>
                  </div>
                  <AnalysisResult data={currentResult} />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
