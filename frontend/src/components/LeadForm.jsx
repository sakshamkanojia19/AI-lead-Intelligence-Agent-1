import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Building2, Target, Loader2, Sparkles } from 'lucide-react'
import { researchLead } from '../services/api'

const LeadForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({ company_name: '', company_domain: '', icp_persona: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      if (!formData.company_name && !formData.company_domain) {
        throw new Error('Please provide company name or domain')
      }
      const result = await researchLead({
        company_name: formData.company_name || null,
        company_domain: formData.company_domain || null,
        icp_persona: formData.icp_persona,
      })
      onSuccess(result)
      setFormData({ company_name: '', company_domain: '', icp_persona: '' })
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white/90 rounded-3xl shadow-xl border border-sand-dark overflow-hidden">
      <div className="bg-gradient-to-r from-ink to-teal-dark p-6 text-sand">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-lg"><Sparkles className="w-6 h-6" /></div>
          <div>
            <h2 className="text-2xl font-bold font-display">AI Lead Intelligence</h2>
            <p className="text-sand/80 text-sm">Research, analyze, and craft outreach in one pass</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-ink flex items-center gap-2">
              <Building2 className="w-4 h-4 text-teal-dark" />Company Name
            </label>
            <input
              type="text"
              placeholder="e.g., Acme Corporation"
              value={formData.company_name}
              onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-sand-dark focus:border-teal-dark focus:ring-2 focus:ring-teal/20 outline-none bg-sand-light"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold text-ink flex items-center gap-2">
              <Search className="w-4 h-4 text-teal-dark" />Domain (optional)
            </label>
            <input
              type="text"
              placeholder="e.g., acme.com"
              value={formData.company_domain}
              onChange={(e) => setFormData({ ...formData, company_domain: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-sand-dark focus:border-teal-dark focus:ring-2 focus:ring-teal/20 outline-none bg-sand-light"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-ink flex items-center gap-2">
            <Target className="w-4 h-4 text-clay" />Target ICP Persona *
          </label>
          <input
            type="text"
            required
            placeholder="e.g., VP of Engineering at Series B SaaS"
            value={formData.icp_persona}
            onChange={(e) => setFormData({ ...formData, icp_persona: e.target.value })}
            className="w-full px-4 py-3 rounded-xl border border-sand-dark focus:border-teal-dark focus:ring-2 focus:ring-teal/20 outline-none bg-sand-light"
          />
        </div>

        {error && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 bg-clay/10 border border-clay/30 rounded-xl text-clay text-sm">
            {error}
          </motion.div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-4 bg-ink text-sand font-semibold rounded-xl hover:shadow-glow transition-all disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? <><Loader2 className="w-5 h-5 animate-spin" />Agent researching...</> : <><Sparkles className="w-5 h-5" />Generate Lead Intelligence</>}
        </button>
      </form>
    </motion.div>
  )
}

export default LeadForm
