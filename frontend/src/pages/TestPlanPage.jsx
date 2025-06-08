import { useState, useEffect } from 'react';
import axios from 'axios';

const TestPlanPage = () => {
  const [testPlans, setTestPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    start_time: '',
    end_time: '',
    status: 'pending',
  });

  useEffect(() => {
    fetchTestPlans();
  }, []);

  const fetchTestPlans = async () => {
    try {
      const response = await axios.get('/api/testplans/');
      setTestPlans(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching test plans:', error);
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/testplans/', formData);
      fetchTestPlans();
      setFormData({
        name: '',
        start_time: '',
        end_time: '',
        status: 'pending',
      });
    } catch (error) {
      console.error('Error creating test plan:', error);
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`/api/testplans/${id}/`);
      fetchTestPlans();
    } catch (error) {
      console.error('Error deleting test plan:', error);
    }
  };

  if (loading) return <div className="text-center">Loading...</div>;

  return (
    <div className="card mb-4">
      <div className="card-header">
        <h2>Test Plans</h2>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit} className="mb-4">
          <div className="mb-3">
            <label className="form-label">Name</label>
            <input type="text" name="name" value={formData.name} onChange={handleInputChange} className="form-control" required />
          </div>
          <div className="mb-3">
            <label className="form-label">Start Time</label>
            <input type="datetime-local" name="start_time" value={formData.start_time} onChange={handleInputChange} className="form-control" />
          </div>
          <div className="mb-3">
            <label className="form-label">End Time</label>
            <input type="datetime-local" name="end_time" value={formData.end_time} onChange={handleInputChange} className="form-control" />
          </div>
          <div className="mb-3">
            <label className="form-label">Status</label>
            <select name="status" value={formData.status} onChange={handleInputChange} className="form-control">
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary">Add Test Plan</button>
        </form>

        <div className="list-group">
          {testPlans.map(plan => (
            <div key={plan.id} className="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <strong>{plan.name}</strong> - {plan.status}
              </div>
              <button onClick={() => handleDelete(plan.id)} className="btn btn-danger btn-sm">Delete</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TestPlanPage; 