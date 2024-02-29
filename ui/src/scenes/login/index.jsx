import Button from '@mui/material/Button';
import CustomInput from '../../components/CustomInput/CustomInput';
const login = () => {
  return (
    <div className="App">
      <form className="form">
        <CustomInput
          labelText="Email"
          id="email"
          formControlProps={{
            fullWidth: true
          }}
          handleChange={this.handleChange}
          type="text"
        />
        <CustomInput
          labelText="Password"
          id="password"
          formControlProps={{
            fullWidth: true
          }}
          handleChange={this.handleChange}
          type="password"
        />
        
        <Button type="button" color="primary" className="form__custom-button">
          Log in
        </Button>
      </form>
    </div>
  );
}