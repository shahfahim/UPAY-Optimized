import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../api/client'
import { useShell } from '../../components/AppShell'
import { Icon } from '../../components/Icon'
import { Card, Spinner, ErrorNote, Button } from '../../components/ui'
import { useLang } from '../../i18n'
import type { NearbyAgent } from '../../api/types'

export default function AgentLocator() {
  const { L } = useLang()
  const { uid } = useShell()
  const navigate = useNavigate()

  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [geoError, setGeoError] = useState<string | null>(null)
  
  const [agents, setAgents] = useState<NearbyAgent[] | null>(null)
  const [loadingAgents, setLoadingAgents] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [activeMapId, setActiveMapId] = useState<string | null>(null)

  useEffect(() => {
    const fallbackLocation = () => {
      setGeoError(L('ডেমো মোড: ডিফল্ট লোকেশন (ঢাকা) দেখানো হচ্ছে।', 'Demo Mode: Showing default location (Dhaka).'))
      setLocation({ lat: 23.8103, lng: 90.4125 })
    }

    if (!navigator.geolocation) {
      fallbackLocation()
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        })
      },
      () => {
        fallbackLocation()
      }
    )
  }, [L])

  useEffect(() => {
    if (location) {
      setLoadingAgents(true)
      setApiError(null)
      api.nearbyAgents(uid, location.lat, location.lng)
        .then(data => {
          setAgents(data)
          setLoadingAgents(false)
        })
        .catch(err => {
          setApiError(err.message || L('এজেন্ট খুঁজতে সমস্যা হচ্ছে।', 'Failed to fetch agents.'))
          setLoadingAgents(false)
        })
    }
  }, [location, uid, L])

  const getStatusColor = (status: string) => {
    if (status === 'green') return 'text-green-600 bg-green-100'
    if (status === 'amber') return 'text-amber-600 bg-amber-100'
    return 'text-red-600 bg-red-100'
  }

  return (
    <div className="min-h-screen bg-slate-50 pb-36 animate-fade-in">
      <div className="bg-upay-blue px-4 pt-12 pb-6 rounded-b-3xl shadow-sm relative">
        <button 
          onClick={() => navigate(-1)} 
          className="absolute left-4 top-12 p-2 -ml-2 text-white/80 hover:text-white"
        >
          <Icon name="chevron-left" size={24} />
        </button>
        <div className="text-center mt-2">
          <h2 className="text-white text-2xl font-bold tracking-tight">
            {L('নিকটস্থ এজেন্ট', 'Nearby Agents')}
          </h2>
          <p className="text-blue-100 text-sm mt-1">
            {L('আপনার আশেপাশের এজেন্ট খুঁজুন', 'Find agents around you')}
          </p>
        </div>
      </div>

      <div className="px-4 mt-6">
        <div className="bg-amber-50 text-amber-700 border border-amber-200 p-3 rounded-xl text-xs mb-4 text-center">
          {L('ডেমো: এগুলো নমুনা এজেন্ট ও নমুনা মান — আসল upay এজেন্ট বা ক্যাশের তথ্য নয়।', 'Demo: sample agents and sample values — not real upay agent or cash data.')}
        </div>
        {!location && !geoError && (
          <div className="flex flex-col items-center justify-center py-16 bg-white rounded-2xl shadow-sm">
            <Spinner label={L('আপনার লোকেশন খোঁজা হচ্ছে...', 'Locating you...')} />
          </div>
        )}

        {geoError && (
          <div className="bg-blue-50/50 text-blue-600 border border-blue-100 p-3 rounded-xl text-sm mb-4 text-center">
            {geoError}
          </div>
        )}

        {loadingAgents && (
          <div className="flex flex-col items-center justify-center py-16 bg-white rounded-2xl shadow-sm mt-4">
            <Spinner label={L('এজেন্টদের খোঁজা হচ্ছে...', 'Finding agents...')} />
          </div>
        )}

        {apiError && !loadingAgents && (
          <ErrorNote message={apiError} />
        )}

        {agents && agents.length === 0 && !loadingAgents && (
          <Card className="text-center py-10 bg-white">
            <Icon name="map-pin" size={32} className="mx-auto text-slate-300 mb-3" />
            <p className="text-slate-500 font-medium">{L('আশেপাশে কোনো এজেন্ট পাওয়া যায়নি।', 'No agents found nearby.')}</p>
          </Card>
        )}

        {agents && agents.length > 0 && !loadingAgents && (
          <div className="space-y-4">
            {agents.map((agent, i) => (
              <Card key={agent.id} className="bg-white border-none shadow-[0_4px_20px_rgb(0,0,0,0.04)] rounded-2xl p-5 animate-slide-up" style={{ animationDelay: `${i * 50}ms` }}>
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-bold text-slate-800 text-lg">{agent.name}</h3>
                    <div className="flex items-center text-slate-500 text-sm mt-0.5">
                      <Icon name="map-pin" size={14} className="mr-1" />
                      <span>{agent.distance_m} m</span>
                    </div>
                  </div>
                  <div className={`px-2.5 py-1 rounded-full text-xs font-semibold ${getStatusColor(agent.cash_status)}`}>
                    {agent.cash_status === 'green' ? L('উচ্চ', 'High') : agent.cash_status === 'amber' ? L('মাঝারি', 'Medium') : L('নিম্ন', 'Low')}
                  </div>
                </div>
                
                <div className="mt-4 bg-slate-50 rounded-xl p-3 border border-slate-100">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-xs font-medium text-slate-600">{L('ক্যাশ থাকার নমুনা মান (ডেমো)', 'Cash hint (demo sample)')}</span>
                    <span className="text-xs font-bold text-slate-700">{(agent.cash_hint * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                    <div 
                      className={`h-1.5 rounded-full ${agent.cash_status === 'green' ? 'bg-green-500' : agent.cash_status === 'amber' ? 'bg-amber-500' : 'bg-red-500'}`}
                      style={{ width: `${agent.cash_hint * 100}%` }}
                    />
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <Button 
                    className="flex-1 !min-h-10 bg-upay-blue hover:bg-blue-700 text-white rounded-xl shadow-sm"
                    onClick={() => setActiveMapId(activeMapId === agent.id ? null : agent.id)}
                  >
                    {activeMapId === agent.id ? L('ম্যাপ বন্ধ করুন', 'Close Map') : L('ম্যাপ দেখুন', 'View Map')}
                  </Button>
                </div>

                {activeMapId === agent.id && (
                  <div className="mt-3 rounded-xl overflow-hidden border border-slate-200 shadow-sm h-48 relative">
                    <iframe
                        width="100%"
                        height="100%"
                        frameBorder="0"
                        src={`https://www.google.com/maps?saddr=${location?.lat},${location?.lng}&daddr=${agent.lat},${agent.lng}&output=embed`}
                        style={{ border: 0 }}
                        allowFullScreen
                      ></iframe>
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
